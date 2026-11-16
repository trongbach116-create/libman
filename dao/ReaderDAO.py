import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database import get_db_connection

class Reader:
    def __init__(self, fullName, birth, address, phone, email, id=None):
        self.id = id
        self.fullName = fullName
        self.birth = birth
        self.address = address
        self.phone = phone
        self.email = email

class ReaderDAO:
    @staticmethod
    def checkReader(reader: Reader) -> bool:
        """
        Kiem tra so dien thoai, email chua ton tai trong tblReader.
        Tra ve True neu hop le (chua ton tai), False neu da ton tai.
        """
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT ID FROM tblReader WHERE phone = ? OR email = ?",
            (reader.phone.strip(), reader.email.strip())
        )
        row = cur.fetchone()
        conn.close()
        return row is None

    @staticmethod
    def saveReader(reader: Reader, username=None, password=None) -> int:
        """
        Ghi du lieu vao tblUser va tblReader. Tra ve readerID.
        """
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Tao tai khoan mac dinh trong tblUser
        user_name = username or reader.email.split('@')[0]
        pass_word = password or "123456"
        
        # Check if username exists, if so append random/id
        cur.execute("SELECT ID FROM tblUser WHERE username = ?", (user_name,))
        if cur.fetchone():
            user_name = f"{user_name}_{reader.phone[-4:]}"

        cur.execute(
            "INSERT INTO tblUser (username, password, fullname, role) VALUES (?, ?, ?, 'reader')",
            (user_name, pass_word, reader.fullName)
        )
        user_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO tblReader (birth, email, phone, address, tblUserID)
            VALUES (?, ?, ?, ?, ?)
            """,
            (reader.birth, reader.email.strip(), reader.phone.strip(), reader.address, user_id)
        )
        reader_id = cur.lastrowid
        conn.commit()
        conn.close()
        return reader_id
