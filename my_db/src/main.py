import os

from cli import (
    get_the_env_parser,
    handle_decryption,
    handle_deletion,
    handle_encryption,
)
from db import DbConnectionPool, create_table


def main():
    db_url = os.getenv("DATABASE_URL", "sqlite:///../metadata.db")
    create_table(DbConnectionPool(db_url).engine())

    args = get_the_env_parser()

    if args.delete:
        print(f"[*] Se inițializează ștergerea pentru: {args.delete}...")
        handle_deletion(args.delete)

    elif args.encrypt:
        print(f"[*] Se inițializează criptarea pentru: {args.encrypt}...")
        handle_encryption(args.encrypt)

    elif args.decrypt:
        print(f"[*] Se inițializează decriptarea pentru: {args.decrypt}...")
        result_path = handle_decryption(args.decrypt)
        if result_path:
            print(f"[*] Succes! Fișierul a fost decriptat la: {result_path}")


if __name__ == "__main__":
    main()
