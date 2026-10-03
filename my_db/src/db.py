import os
from pathlib import Path

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

import delete

load_dotenv()


class DbConnectionPool:
    _instance = None

    def __new__(cls, db_url: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            if ":memory:" in db_url:
                cls._instance.pool_engine = create_engine(db_url)
            else:
                cls._instance.pool_engine = create_engine(
                    db_url, pool_size=5, max_overflow=10
                )
        return cls._instance

    def engine(self) -> sqlalchemy.Engine:
        return self.pool_engine


def create_table(engine: sqlalchemy.Engine):
    with engine.connect() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    original_filename TEXT, 
                    encrypted_file_path TEXT, 
                    encryption_method TEXT, 
                    key_id TEXT
                )
                """
            )
        )
        connection.commit()


def build_db_data(
    original_filename: str,
    encryption_method: str,
    encrypted_file_path: str,
    key_id: str,
):
    return (original_filename, encrypted_file_path, encryption_method, key_id)


def store_file(data: list[str]):
    # Luăm URL-ul din .env. Dacă nu există, folosim un default de siguranță.
    db_url = os.getenv("DATABASE_URL", "sqlite:///../metadata.db")
    pool = DbConnectionPool(db_url)

    with pool.engine().connect() as connection:
        connection.execute(
            text(
                """
                INSERT INTO files(original_filename, encrypted_file_path, encryption_method, key_id) 
                VALUES(:orig_file, :enc_file, :enc_method, :k_id)
                """
            ),
            [
                {
                    "orig_file": row[0],
                    "enc_file": row[1],
                    "enc_method": row[2],
                    "k_id": row[3],
                }
                for row in data
            ],
        )
        connection.commit()


def get_file_info(file_name: str):
    db_url = os.getenv("DATABASE_URL", "sqlite:///../metadata.db")
    pool = DbConnectionPool(db_url)

    with pool.engine().connect() as connection:
        result = connection.execute(
            text(
                "SELECT original_filename, encrypted_file_path, encryption_method, key_id FROM files WHERE original_filename = :f_name"
            ),
            {"f_name": file_name},
        )
        row = result.fetchone()

        if row:
            print(f"Am găsit fișierul: {row[0]}")
            return row
        else:
            print("Fișierul nu a fost găsit în baza de date.")
            return None


def delete_entry_file(file_name_to_delete: str):
    db_url = os.getenv("DATABASE_URL", "sqlite:///../metadata.db")
    pool = DbConnectionPool(db_url)

    with pool.engine().connect() as connection:
        result = connection.execute(
            text(
                "SELECT encrypted_file_path, key_id FROM files WHERE original_filename = :f_name"
            ),
            {"f_name": file_name_to_delete},
        )
        row = result.fetchone()

        if not row:
            print("Eroare: Fișierul nu a fost găsit în baza de date.")
            return

        enc_path = row[0]
        k_id = row[1]

        delete.delete_entry(enc_path, k_id)
        print("Ștergerea fizică a funcționat.")

        connection.execute(
            text("DELETE FROM files WHERE original_filename = :f_name"),
            {"f_name": file_name_to_delete},
        )
        connection.commit()
        print("Ștergerea din baza de date a funcționat.")
