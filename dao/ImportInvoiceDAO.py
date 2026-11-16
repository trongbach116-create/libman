import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_db_connection

class ImportInvoice:
    def __init__(self, id, code, importDate, staffName, totalQuantity, totalAmount, supplierID=None, supplierName=None):
        self.id = id
        self.code = code
        self.importDate = importDate
        self.staffName = staffName
        self.totalQuantity = totalQuantity
        self.totalAmount = totalAmount
        self.supplierID = supplierID
        self.supplierName = supplierName

class ImportInvoiceDAO:
    @staticmethod
    def getImportInvoiceBySupplier(supplierID: int, startDate: str, endDate: str):
        """
        Lay danh sach hoa don nhap cua mot nha cung cap trong khoang thoi gian duoc chon.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                inv.ID as invoiceID,
                inv.code as invoiceCode,
                inv.date as importDate,
                u.fullname as staffName,
                s.name as supplierName,
                COALESCE(SUM(d.quantity), 0) as totalQuantity,
                COALESCE(SUM(d.quantity * d.unitPrice), 0) as totalAmount
            FROM tblImportInvoice inv
            JOIN tblSupplier s ON inv.tblSupplierID = s.ID
            JOIN tblStaff st ON inv.tblStaffID = st.ID
            JOIN tblUser u ON st.tblUserID = u.ID
            LEFT JOIN tblImportDetail d ON inv.ID = d.tblImportInvoiceID
            WHERE inv.tblSupplierID = ? AND inv.date >= ? AND inv.date <= ?
            GROUP BY inv.ID, inv.code, inv.date, u.fullname, s.name
            ORDER BY inv.date ASC
        """
        cur.execute(query, (supplierID, startDate, endDate))
        rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            inv = ImportInvoice(
                id=r['invoiceID'],
                code=r['invoiceCode'],
                importDate=r['importDate'],
                staffName=r['staffName'],
                totalQuantity=r['totalQuantity'],
                totalAmount=r['totalAmount'],
                supplierID=supplierID,
                supplierName=r['supplierName']
            )
            result.append(inv)
        return result

    @staticmethod
    def getInvoiceByID(invoiceID: int):
        """
        Lay thong tin mot hoa don nhap theo ID.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                inv.ID as invoiceID,
                inv.code as invoiceCode,
                inv.date as importDate,
                u.fullname as staffName,
                s.name as supplierName,
                COALESCE(SUM(d.quantity), 0) as totalQuantity,
                COALESCE(SUM(d.quantity * d.unitPrice), 0) as totalAmount
            FROM tblImportInvoice inv
            JOIN tblSupplier s ON inv.tblSupplierID = s.ID
            JOIN tblStaff st ON inv.tblStaffID = st.ID
            JOIN tblUser u ON st.tblUserID = u.ID
            LEFT JOIN tblImportDetail d ON inv.ID = d.tblImportInvoiceID
            WHERE inv.ID = ?
            GROUP BY inv.ID, inv.code, inv.date, u.fullname, s.name
        """
        cur.execute(query, (invoiceID,))
        r = cur.fetchone()
        conn.close()

        if r:
            return ImportInvoice(
                id=r['invoiceID'],
                code=r['invoiceCode'],
                importDate=r['importDate'],
                staffName=r['staffName'],
                totalQuantity=r['totalQuantity'],
                totalAmount=r['totalAmount'],
                supplierName=r['supplierName']
            )
        return None
