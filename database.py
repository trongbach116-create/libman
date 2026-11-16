import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'libman.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Drop existing tables to start fresh
    cur.executescript('''
    DROP TABLE IF EXISTS tblImportDetail;
    DROP TABLE IF EXISTS tblImportInvoice;
    DROP TABLE IF EXISTS tblDocument;
    DROP TABLE IF EXISTS tblSupplier;
    DROP TABLE IF EXISTS tblReader;
    DROP TABLE IF EXISTS tblStaff;
    DROP TABLE IF EXISTS tblUser;

    -- tblUser
    CREATE TABLE tblUser (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL,
        role TEXT NOT NULL
    );

    -- tblStaff
    CREATE TABLE tblStaff (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        position TEXT,
        tblUserID INTEGER NOT NULL,
        FOREIGN KEY (tblUserID) REFERENCES tblUser(ID)
    );

    -- tblReader
    CREATE TABLE tblReader (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        birth TEXT,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        address TEXT,
        cardCode TEXT UNIQUE,
        cardIssueDate TEXT,
        cardExpiryDate TEXT,
        cardStatus TEXT,
        tblUserID INTEGER,
        FOREIGN KEY (tblUserID) REFERENCES tblUser(ID)
    );

    -- tblSupplier
    CREATE TABLE tblSupplier (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        address TEXT,
        phone TEXT,
        email TEXT
    );

    -- tblDocument
    CREATE TABLE tblDocument (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        author TEXT,
        publishYear INTEGER,
        publisher TEXT,
        type TEXT,
        position TEXT
    );

    -- tblImportInvoice
    CREATE TABLE tblImportInvoice (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        tblStaffID INTEGER NOT NULL,
        tblSupplierID INTEGER NOT NULL,
        FOREIGN KEY (tblStaffID) REFERENCES tblStaff(ID),
        FOREIGN KEY (tblSupplierID) REFERENCES tblSupplier(ID)
    );

    -- tblImportDetail
    CREATE TABLE tblImportDetail (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        quantity INTEGER NOT NULL,
        unitPrice REAL NOT NULL,
        tblImportInvoiceID INTEGER NOT NULL,
        tblDocumentID INTEGER NOT NULL,
        FOREIGN KEY (tblImportInvoiceID) REFERENCES tblImportInvoice(ID),
        FOREIGN KEY (tblDocumentID) REFERENCES tblDocument(ID)
    );
    ''')

    # Seed Users & Staff
    cur.execute("INSERT INTO tblUser (username, password, fullname, role) VALUES ('quanly', '123456', 'Nguyễn Quản Lý', 'management')")
    cur.execute("INSERT INTO tblUser (username, password, fullname, role) VALUES ('nhanvien1', '123456', 'Nguyễn Văn A', 'staff')")
    staff_user_id1 = cur.lastrowid
    cur.execute("INSERT INTO tblStaff (phone, position, tblUserID) VALUES ('0912345678', 'Thủ thư', ?)", (staff_user_id1,))
    staff_id1 = cur.lastrowid

    cur.execute("INSERT INTO tblUser (username, password, fullname, role) VALUES ('nhanvien2', '123456', 'Trần Thị B', 'staff')")
    staff_user_id2 = cur.lastrowid
    cur.execute("INSERT INTO tblStaff (phone, position, tblUserID) VALUES ('0987654321', 'Thủ thư', ?)", (staff_user_id2,))
    staff_id2 = cur.lastrowid

    # Seed Sample Reader
    cur.execute("INSERT INTO tblUser (username, password, fullname, role) VALUES ('docgia1', '123456', 'Trần Văn Độc Giả', 'reader')")
    reader_user_id = cur.lastrowid
    cur.execute("""
        INSERT INTO tblReader (birth, email, phone, address, cardCode, cardIssueDate, cardExpiryDate, cardStatus, tblUserID)
        VALUES ('2003-05-15', 'docgia@ptit.edu.vn', '0901234567', 'Hà Nội', 'RC2026000', '2026-01-01', '2027-01-01', 'active', ?)
    """, (reader_user_id,))

    # Seed Suppliers (from document page 28: S01, S02, S03)
    suppliers = [
        ('S01', 'Nhà sách Giáo dục', 'Hà Nội', '02438220801', 'giaoduc@nxb.vn'),
        ('S02', 'Công ty Sách Thành Nghĩa', 'TP. Hồ Chí Minh', '02838300400', 'thanhnghia@sach.vn'),
        ('S03', 'NXB Khoa học Kỹ thuật', 'Hà Nội', '02438221800', 'khkt@nxb.vn'),
        ('S04', 'NXB Kim Đồng', 'Hà Nội', '02439434730', 'kimdong@nxb.vn'),
        ('S05', 'NXB Trẻ', 'TP. Hồ Chí Minh', '02839316289', 'nxbtre@nxbtre.com.vn')
    ]
    cur.executemany("INSERT INTO tblSupplier (code, name, address, phone, email) VALUES (?, ?, ?, ?, ?)", suppliers)

    # Seed Documents
    documents = [
        ('D001', 'Cơ sở dữ liệu', 'Đỗ Trung Tuấn', 2022, 'NXB Giáo Dục', 'Giáo trình', 'Kệ A1-01'),
        ('D014', 'Lập trình hướng đối tượng', 'Nguyễn Mạnh Hùng', 2023, 'NXB Khoa học Kỹ thuật', 'Sách', 'Kệ B2-05'),
        ('D027', 'Tạp chí Bưu chính Viễn thông', 'Bộ Thông tin và Truyền thông', 2024, 'NXB Thông tin', 'Tạp chí', 'Kệ C1-10'),
        ('D030', 'Kỹ thuật lập trình Web', 'Phạm Văn Ất', 2022, 'NXB Giáo Dục', 'Giáo trình', 'Kệ A2-03'),
        ('D035', 'Trí tuệ nhân tạo căn bản', 'Lê Hoài Bắc', 2023, 'NXB Đại học Quốc gia', 'Sách', 'Kệ D3-12')
    ]
    cur.executemany("INSERT INTO tblDocument (code, name, author, publishYear, publisher, type, position) VALUES (?, ?, ?, ?, ?, ?, ?)", documents)

    # Seed Invoices for S01 (matches document page 28 and 29)
    # HD001: 2026-01-05 (05/01/2026), Nguyễn Văn A, Total Qty: 50, Total: 7,500,000
    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD001', '2026-01-05', ?, 1)", (staff_id1,))
    inv1_id = cur.lastrowid
    # HD001 details: D001 (20 * 150k = 3M), D014 (15 * 150k = 2.25M), D027 (15 * 150k = 2.25M)
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (20, 150000, ?, 1)", (inv1_id,))
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (15, 150000, ?, 2)", (inv1_id,))
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (15, 150000, ?, 3)", (inv1_id,))

    # HD005: 2026-02-18 (18/02/2026), Trần Thị B, Total Qty: 80, Total: 12,000,000
    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD005', '2026-02-18', ?, 1)", (staff_id2,))
    inv5_id = cur.lastrowid
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (40, 150000, ?, 1)", (inv5_id,))
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (40, 150000, ?, 4)", (inv5_id,))

    # HD009: 2026-04-10 (10/04/2026), Nguyễn Văn A, Total Qty: 190, Total: 28,500,000
    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD009', '2026-04-10', ?, 1)", (staff_id1,))
    inv9_id = cur.lastrowid
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (100, 150000, ?, 2)", (inv9_id,))
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (90, 150000, ?, 5)", (inv9_id,))

    # Invoices for S02 (Total Qty: 150, Total: 22,500,000, Invoices: 3)
    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD012', '2026-01-15', ?, 2)", (staff_id1,))
    inv12_id = cur.lastrowid
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (50, 150000, ?, 2)", (inv12_id,))

    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD015', '2026-03-20', ?, 2)", (staff_id2,))
    inv15_id = cur.lastrowid
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (50, 150000, ?, 3)", (inv15_id,))

    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD018', '2026-05-12', ?, 2)", (staff_id1,))
    inv18_id = cur.lastrowid
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (50, 150000, ?, 4)", (inv18_id,))

    # Invoices for S03 (Total Qty: 90, Total: 13,200,000, Invoices: 2)
    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD021', '2026-02-10', ?, 3)", (staff_id1,))
    inv21_id = cur.lastrowid
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (40, 140000, ?, 2)", (inv21_id,))
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (10, 200000, ?, 5)", (inv21_id,))

    cur.execute("INSERT INTO tblImportInvoice (code, date, tblStaffID, tblSupplierID) VALUES ('HD025', '2026-06-01', ?, 3)", (staff_id2,))
    inv25_id = cur.lastrowid
    cur.execute("INSERT INTO tblImportDetail (quantity, unitPrice, tblImportInvoiceID, tblDocumentID) VALUES (40, 140000, ?, 1)", (inv25_id,))

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
