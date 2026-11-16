import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_db_connection

class SupplierStat:
    def __init__(self, supplierID, code, name, totalInvoice, totalQuantity, totalAmount):
        self.supplierID = supplierID
        self.code = code
        self.name = name
        self.totalInvoice = totalInvoice
        self.totalQuantity = totalQuantity
        self.totalAmount = totalAmount

class SupplierDAO:
    @staticmethod
    def getSupplierStat(startDate: str, endDate: str):
        """
        Truy van tblSupplier, tblImportInvoice, tblImportDetail trong khoang thoi gian,
        tinh totalInvoice, totalQuantity, totalAmount cho tung nha cung cap va tao cac doi tuong SupplierStat.
        startDate, endDate co dinh dang YYYY-MM-DD.
        """
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                s.ID as supplierID,
                s.code as supplierCode,
                s.name as supplierName,
                COUNT(DISTINCT inv.ID) as totalInvoice,
                COALESCE(SUM(d.quantity), 0) as totalQuantity,
                COALESCE(SUM(d.quantity * d.unitPrice), 0) as totalAmount
            FROM tblSupplier s
            INNER JOIN tblImportInvoice inv ON s.ID = inv.tblSupplierID
            LEFT JOIN tblImportDetail d ON inv.ID = d.tblImportInvoiceID
            WHERE inv.date >= ? AND inv.date <= ?
            GROUP BY s.ID, s.code, s.name
            HAVING totalInvoice > 0
            ORDER BY totalQuantity DESC
        """
        cur.execute(query, (startDate, endDate))
        rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            stat = SupplierStat(
                supplierID=r['supplierID'],
                code=r['supplierCode'],
                name=r['supplierName'],
                totalInvoice=r['totalInvoice'],
                totalQuantity=r['totalQuantity'],
                totalAmount=r['totalAmount']
            )
            result.append(stat)
        return result

    @staticmethod
    def getSupplierByID(supplierID: int):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tblSupplier WHERE ID = ?", (supplierID,))
        row = cur.fetchone()
        conn.close()
        return row
