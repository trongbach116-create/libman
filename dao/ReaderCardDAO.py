import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_db_connection

class ReaderCard:
    def __init__(self, cardCode, issueDate, expiryDate, status="active", readerId=None):
        self.cardCode = cardCode
        self.issueDate = issueDate
        self.expiryDate = expiryDate
        self.status = status
        self.readerId = readerId

class ReaderCardDAO:
    @staticmethod
    def generateID() -> str:
        """
        Sinh ma the moi dang RCYYYYxxx (vi du: RC2026001)
        """
        conn = get_db_connection()
        cur = conn.cursor()
        year = datetime.now().year
        prefix = f"RC{year}"
        
        cur.execute("SELECT cardCode FROM tblReader WHERE cardCode LIKE ? ORDER BY cardCode DESC LIMIT 1", (f"{prefix}%",))
        row = cur.fetchone()
        conn.close()

        if row and row['cardCode']:
            try:
                last_num = int(row['cardCode'][len(prefix):])
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        return f"{prefix}{next_num:03d}"

    @staticmethod
    def saveCard(readerId: int, card: ReaderCard) -> bool:
        """
        Luu thong tin the (cardCode, cardIssueDate, cardExpiryDate, cardStatus) vao tblReader
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE tblReader
            SET cardCode = ?, cardIssueDate = ?, cardExpiryDate = ?, cardStatus = ?
            WHERE ID = ?
            """,
            (card.cardCode, card.issueDate, card.expiryDate, card.status, readerId)
        )
        conn.commit()
        success = cur.rowcount > 0
        conn.close()
        return success
