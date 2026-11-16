import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_db_connection

class ImportedDocument:
    def __init__(self, id, docCode, docName, docType, quantity, unitPrice, amount):
        self.id = id
        self.docCode = docCode
        self.docName = docName
        self.docType = docType
        self.quantity = quantity
        self.unitPrice = unitPrice
        self.amount = amount

class ImportedDocumentDAO:
    @staticmethod
    def getByInvoice(invoiceID: int):
        """
        Truy van tblImportDetail ket hop tblDocument, tra ve List<ImportedDocument>
        """
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                d.ID as detailID,
                doc.code as docCode,
                doc.name as docName,
                doc.type as docType,
                d.quantity as quantity,
                d.unitPrice as unitPrice,
                (d.quantity * d.unitPrice) as amount
            FROM tblImportDetail d
            JOIN tblDocument doc ON d.tblDocumentID = doc.ID
            WHERE d.tblImportInvoiceID = ?
            ORDER BY doc.code ASC
        """
        cur.execute(query, (invoiceID,))
        rows = cur.fetchall()
        conn.close()

        result = []
        for r in rows:
            item = ImportedDocument(
                id=r['detailID'],
                docCode=r['docCode'],
                docName=r['docName'],
                docType=r['docType'],
                quantity=r['quantity'],
                unitPrice=r['unitPrice'],
                amount=r['amount']
            )
            result.append(item)
        return result
