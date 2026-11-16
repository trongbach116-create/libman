# Hệ Thống Quản Lý Thư Viện Đại Học (LibMan) - Subject No. 06

Dự án được xây dựng bám sát chính xác tài liệu đặc tả, thiết kế ca sử dụng (Use case), biểu đồ lớp chi tiết (Class Diagram), biểu đồ trình tự (Sequence Diagram), kịch bản (Scenario v3.0) và thiết kế giao diện (UI Wireframe).

---

## 🎯 2 Module thiết yếu được hiện thực hóa

### 1. Module 1: Độc giả đăng ký thẻ trực tuyến (`Reader registers for a reader card`)
- **Giao diện chính độc giả (`ReaderHomeFrm`)**:
  - Lời chào độc giả, các nút điều hướng.
  - Nút **"Đăng ký thẻ độc giả"** (`btnRegisterCard`).
- **Giao diện biểu mẫu đăng ký (`RegisterCardFrm`)**:
  - Nhóm thông tin độc giả: Họ tên (`txtFullname`), Ngày sinh (`txtBirth`), Địa chỉ (`txtAddress`), Điện thoại (`txtPhone`), Email (`txtEmail`).
  - Nhóm thông tin thẻ: Mã thẻ (`txtID` tự sinh dạng `RCYYYYxxx`), Ngày đăng ký (`txtIssueDate`), Ngày hết hạn (`txtExpiryDate`).
  - Nút **Lưu** (`btnSave`) và **Hủy** (`btnCancel`).
- **Xử lý nghiệp vụ & Ngoại lệ**:
  - `ReaderDAO.checkReader(reader)`: Kiểm tra trùng lặp SĐT hoặc Email (Ngoại lệ **7a**).
  - Kiểm tra hợp lệ các trường bắt buộc và định dạng (Ngoại lệ **5a**).
  - `ReaderCardDAO.generateID()` & `saveCard(card)`: Tự sinh mã thẻ và ghi nhận vào CSDL.
  - Hiển thị hộp thoại Modal thông báo kết quả: *"Đăng ký thẻ độc giả thành công! Mã thẻ của bạn: RC2026001"*.

---

### 2. Module 2: Quản lý xem thống kê nhà cung cấp theo khối lượng nhập (`Management staff views supplier statistics`)
- **Giao diện trang chủ quản lý (`ManagerHomeFrm`)**:
  - Nút **"Xem báo cáo thống kê"** (`btnViewReport`).
- **Menu báo cáo (`StatMenuFrm`)**:
  - Nút chọn chức năng **"Thống kê nhà cung cấp theo số lượng nhập"** (`btnSupplierStat`).
- **Thống kê nhà cung cấp (`SupplierStatFrm`)**:
  - Thiết lập khoảng thời gian: Từ ngày (`txtStartDate`), Đến ngày (`txtEndDate`), Nút Xem (`btnView`).
  - Bảng thống kê `tblSupplierStat`: `STT | Mã NCC | Tên nhà cung cấp | Số hóa đơn | Tổng SL nhập | Tổng tiền`.
  - Xử lý ngoại lệ **8a** (Ngày bắt đầu > Ngày kết thúc), ngoại lệ **10a** (Không có NCC nào nhập hàng).
  - Cho phép nhấp chọn một dòng nhà cung cấp (`btnSupplierRow`) để chuyển sang danh sách hóa đơn.
- **Danh sách hóa đơn nhập của NCC (`ImportInvoiceListFrm`)**:
  - Thông tin tên nhà cung cấp, khoảng thời gian.
  - Bảng hóa đơn `tblInvoice`: `STT | Mã HĐ | Ngày nhập | Nhân viên nhập | Số lượng | Tổng tiền`.
  - Cho phép nhấp chọn một dòng hóa đơn (`btnInvoiceRow`) để xem chi tiết.
- **Chi tiết hóa đơn nhập (`ImportInvoiceDetailFrm`)**:
  - Thông tin: Mã HĐ, Tên NCC, Ngày nhập, Nhân viên nhập.
  - Bảng chi tiết `tblImportedDoc`: `STT | Mã TL | Tên tài liệu | Loại | SL | Đơn giá | Thành tiền`.
  - Thanh tổng kết: **Tổng số lượng** và **Tổng tiền**.
  - Nút **Quay lại** (`btnBack`) trên từng giao diện để quay lại màn hình trước.

---

## 🛠️ Cấu trúc thư mục mã nguồn

```
libman/
├── database.py              # Khởi tạo CSDL SQLite & seed dữ liệu mẫu chuẩn theo tài liệu
├── libman.db                # File cơ sở dữ liệu SQLite
├── app.py                   # Ứng dụng Flask điều hướng các Module và Route
├── dao/
│   ├── __init__.py
│   ├── ReaderDAO.py         # Xử lý truy vấn bảng tblUser & tblReader
│   ├── ReaderCardDAO.py     # Tự sinh mã thẻ & lưu thẻ độc giả
│   ├── SupplierDAO.py       # Thống kê NCC theo khối lượng nhập
│   ├── ImportInvoiceDAO.py  # Truy vấn danh sách hóa đơn theo NCC
│   └── ImportedDocumentDAO.py # Truy vấn chi tiết hóa đơn & tài liệu nhập
├── templates/
│   ├── base.html            # Khung giao diện dùng chung
│   ├── index.html           # Cổng chọn phân hệ (Độc giả / Quản lý)
│   ├── reader/
│   │   ├── home.html        # ReaderHomeFrm
│   │   └── register.html    # RegisterCardFrm
│   └── manager/
│       ├── home.html        # ManagerHomeFrm
│       ├── stat_menu.html   # StatMenuFrm
│       ├── supplier_stat.html      # SupplierStatFrm
│       ├── invoice_list.html       # ImportInvoiceListFrm
│       └── invoice_detail.html     # ImportInvoiceDetailFrm
└── static/
    └── css/
        └── style.css        # Giao diện sắc nét, trực quan theo wireframe
```

---

## 🚀 Hướng dẫn khởi chạy

1. Cài đặt thư viện:
   ```bash
   pip install flask
   ```

2. Khởi tạo cơ sở dữ liệu (đã có sẵn seed mẫu):
   ```bash
   python database.py
   ```

3. Khởi động Web server:
   ```bash
   python app.py
   ```

4. Mở trình duyệt và truy cập:
   👉 **http://127.0.0.1:5000**
