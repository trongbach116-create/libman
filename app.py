from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import re
import os

from database import init_db, DB_PATH
from dao.ReaderDAO import Reader, ReaderDAO
from dao.ReaderCardDAO import ReaderCard, ReaderCardDAO
from dao.SupplierDAO import SupplierDAO
from dao.ImportInvoiceDAO import ImportInvoiceDAO
from dao.ImportedDocumentDAO import ImportedDocumentDAO

app = Flask(__name__)
app.secret_key = 'libman_secret_key_subject_06'

# Helper function to format date from YYYY-MM-DD to DD/MM/YYYY for display
def format_date_display(date_str):
    if not date_str:
        return ""
    try:
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except Exception:
        pass
    return date_str

@app.route('/')
def index():
    return render_template('index.html')

# =========================================================================
# MODULE 1: Độc giả đăng ký thẻ trực tuyến (Reader registers for a reader card)
# =========================================================================

@app.route('/reader/home')
def reader_home():
    """Giao diện chính của độc giả (ReaderHomeFrm)"""
    return render_template('reader/home.html', 
                           reader_name="Trần Văn Độc Giả", 
                           active_module="reader")

@app.route('/reader/register', methods=['GET', 'POST'])
def reader_register():
    """Giao diện đăng ký thẻ độc giả (RegisterCardFrm)"""
    today = datetime.now()
    issue_date_display = today.strftime("%d/%m/%Y")
    issue_date_db = today.strftime("%Y-%m-%d")
    default_expiry_db = (today + timedelta(days=365)).strftime("%Y-%m-%d")
    generated_code = ReaderCardDAO.generateID()

    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        birth = request.form.get('birth', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        expiry_date = request.form.get('expiry_date', '').strip()

        form_data = {
            'fullname': fullname,
            'birth': birth,
            'address': address,
            'phone': phone,
            'email': email
        }

        # Kiem tra ngoai le 5a: Thieu truong bat buoc hoac sai dinh dang
        if not fullname or not birth or not address or not phone or not email or not expiry_date:
            flash("Lỗi 5a: Vui lòng điền đầy đủ tất cả các trường bắt buộc!", "danger")
            return render_template('reader/register.html', 
                                   generated_code=generated_code,
                                   issue_date=issue_date_display,
                                   expiry_date=expiry_date or default_expiry_db,
                                   form_data=form_data,
                                   active_module="reader")

        # Kiem tra dinh dang email & sdt co ban
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            flash("Lỗi 5a: Định dạng email không hợp lệ!", "danger")
            return render_template('reader/register.html', 
                                   generated_code=generated_code,
                                   issue_date=issue_date_display,
                                   expiry_date=expiry_date,
                                   form_data=form_data,
                                   active_module="reader")

        if not re.match(r"^[0-9]{9,11}$", phone):
            flash("Lỗi 5a: Số điện thoại phải gồm 9-11 chữ số!", "danger")
            return render_template('reader/register.html', 
                                   generated_code=generated_code,
                                   issue_date=issue_date_display,
                                   expiry_date=expiry_date,
                                   form_data=form_data,
                                   active_module="reader")

        # Kiem tra ngoai le 7a: checkReader tra ve false (so dien thoai hoac email da ton tai)
        new_reader = Reader(fullName=fullname, birth=birth, address=address, phone=phone, email=email)
        if not ReaderDAO.checkReader(new_reader):
            flash("Lỗi 7a: Số điện thoại hoặc Email này đã được đăng ký trong hệ thống!", "danger")
            return render_template('reader/register.html', 
                                   generated_code=generated_code,
                                   issue_date=issue_date_display,
                                   expiry_date=expiry_date,
                                   form_data=form_data,
                                   active_module="reader")

        try:
            # Luu Reader vao CSDL
            reader_id = ReaderDAO.saveReader(new_reader)
            
            # Sinh ma the & luu the
            card_code = ReaderCardDAO.generateID()
            card = ReaderCard(
                cardCode=card_code,
                issueDate=issue_date_db,
                expiryDate=expiry_date,
                status="active"
            )
            ReaderCardDAO.saveCard(reader_id, card)

            # Tra ve giao dien kem popup thong bao thanh cong (Scenario buoc 15)
            return render_template('reader/register.html', 
                                   generated_code=card_code,
                                   issue_date=issue_date_display,
                                   expiry_date=expiry_date,
                                   success_card_code=card_code,
                                   active_module="reader")
        except Exception as e:
            flash(f"Lỗi 12a/14a: Lỗi lưu dữ liệu: {str(e)}", "danger")
            return render_template('reader/register.html', 
                                   generated_code=generated_code,
                                   issue_date=issue_date_display,
                                   expiry_date=expiry_date,
                                   form_data=form_data,
                                   active_module="reader")

    return render_template('reader/register.html', 
                           generated_code=generated_code,
                           issue_date=issue_date_display,
                           expiry_date=default_expiry_db,
                           active_module="reader")

# =========================================================================
# MODULE 2: Nhân viên quản lý xem thống kê nhà cung cấp (Management staff views supplier statistics)
# =========================================================================

@app.route('/manager/home')
def manager_home():
    """Giao diện chính của nhân viên quản lý (ManagerHomeFrm)"""
    return render_template('manager/home.html', 
                           manager_name="Nguyễn Quản Lý", 
                           active_module="manager")

@app.route('/manager/stat-menu')
def stat_menu():
    """Menu chọn loại báo cáo thống kê (StatMenuFrm)"""
    return render_template('manager/stat_menu.html', active_module="manager")

@app.route('/manager/stats/supplier')
def supplier_stat():
    """Giao diện xem thống kê nhà cung cấp theo số lượng nhập (SupplierStatFrm)"""
    start_date = request.args.get('start_date', '2026-01-01')
    end_date = request.args.get('end_date', '2026-06-30')
    searched = 'start_date' in request.args

    # Kiem tra ngoai le 8a: Ngay bat dau sau ngay ket thuc
    if start_date and end_date and start_date > end_date:
        flash("Lỗi 8a: Khoảng thời gian không hợp lệ! Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.", "danger")
        return render_template('manager/supplier_stat.html', 
                               start_date=start_date, 
                               end_date=end_date, 
                               stats=[], 
                               searched=True,
                               active_module="manager")

    stats = SupplierDAO.getSupplierStat(start_date, end_date)

    # Ngoai le 10a: Khong co nha cung cap nao nhap hang trong khoang thoi gian
    if searched and len(stats) == 0:
        flash("Ngoại lệ 10a: Không có nhà cung cấp nào nhập hàng trong khoảng thời gian đã chọn.", "info")

    return render_template('manager/supplier_stat.html',
                           start_date=start_date,
                           end_date=end_date,
                           display_start=format_date_display(start_date),
                           display_end=format_date_display(end_date),
                           stats=stats,
                           searched=searched,
                           active_module="manager")

@app.route('/manager/stats/supplier/<int:supplier_id>/invoices')
def invoice_list(supplier_id):
    """Giao diện xem danh sách hóa đơn nhập của nhà cung cấp (ImportInvoiceListFrm)"""
    start_date = request.args.get('start_date', '2026-01-01')
    end_date = request.args.get('end_date', '2026-06-30')

    supplier = SupplierDAO.getSupplierByID(supplier_id)
    invoices = ImportInvoiceDAO.getImportInvoiceBySupplier(supplier_id, start_date, end_date)

    # Dinh dang ngay hien thi
    for inv in invoices:
        inv.importDate = format_date_display(inv.importDate)

    return render_template('manager/invoice_list.html',
                           supplier=supplier,
                           invoices=invoices,
                           start_date=start_date,
                           end_date=end_date,
                           display_start=format_date_display(start_date),
                           display_end=format_date_display(end_date),
                           active_module="manager")

@app.route('/manager/stats/invoices/<int:invoice_id>')
def invoice_detail(invoice_id):
    """Giao diện xem chi tiết hóa đơn nhập (ImportInvoiceDetailFrm)"""
    supplier_id = request.args.get('supplier_id')
    start_date = request.args.get('start_date', '2026-01-01')
    end_date = request.args.get('end_date', '2026-06-30')

    invoice = ImportInvoiceDAO.getInvoiceByID(invoice_id)
    if not invoice:
        flash("Không tìm thấy thông tin hóa đơn!", "danger")
        return redirect(url_for('supplier_stat', start_date=start_date, end_date=end_date))

    invoice.importDate = format_date_display(invoice.importDate)
    details = ImportedDocumentDAO.getByInvoice(invoice_id)

    return render_template('manager/invoice_detail.html',
                           invoice=invoice,
                           details=details,
                           supplier_id=supplier_id,
                           start_date=start_date,
                           end_date=end_date,
                           active_module="manager")

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    print("LibMan Server starting on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
