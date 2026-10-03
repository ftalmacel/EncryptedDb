import argparse
from pathlib import Path

from db import delete_entry_file, get_file_info
from decryption import decryption
from encryption import encryption


def get_the_env_parser():
    parser = _return_parser()

    args = parser.parse_args()

    return args


def _return_parser():
    parser = argparse.ArgumentParser(
        prog="eddb",
        description="This program helps you safely encrypt the important files and then when you need them decrypt it using RSA",
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-v",
        "--delete",
        metavar="FILENAME",
        help="Delete a file from the system and database",
    )
    group.add_argument(
        "-e",
        "--encrypt",
        metavar="FILEPATH",
        help="Encrypt a file and save its metadata",
    )
    group.add_argument(
        "-d", "--decrypt", metavar="FILENAME", help="Decrypt a file and see its content"
    )

    return parser


def handle_deletion(file_name: str):
    print(f"Inițializare ștergere pentru: {file_name}...")
    delete_entry_file(file_name)


def handle_encryption(file_path: str):
    print(f"Inițializare criptare pentru: {file_path}...")
    encryption.encryption(Path(file_path))


def handle_decryption(file_name: str):
    print(f"Inițializare decriptare pentru: {file_name}...")
    row = get_file_info(file_name)

    if not row:
        return

    decrypted_file_path = decryption.decryption(
        original_filename=row[0],
        encrypted_file_path=row[1],
        encryption_method=row[2],
        key_id=row[3],
    )

    if decrypted_file_path:
        print(f"Fișier decriptat salvat la: {decrypted_file_path}")
