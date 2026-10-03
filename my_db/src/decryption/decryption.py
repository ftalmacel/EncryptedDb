import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv()


def decrypt_file(private_key_path: Path, encrypted_file_path: str):
    # Preluăm parola și o transformăm în bytes
    password = os.getenv("PASSWORD").encode("utf-8")

    with open(private_key_path, "rb") as file_key:
        private_key = serialization.load_pem_private_key(
            file_key.read(), password=password
        )
        with open(encrypted_file_path, "rb") as encrypted_file:
            plaintext = private_key.decrypt(
                encrypted_file.read(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return plaintext


def decryption(
    original_filename: str,
    encrypted_file_path: str,
    encryption_method: str,
    key_id: str,
):
    key_dir = Path("../key_dir")
    private_key_path = key_dir / f"{key_id}_private.pem"

    if not private_key_path.exists():
        print(f"Eroare: Cheia privată pentru {original_filename} nu a fost găsită!")
        return None

    plaintext = decrypt_file(private_key_path, encrypted_file_path)

    decrypted_path = Path(f"../decrypted_{original_filename}")
    with open(decrypted_path, "wb") as out_file:
        out_file.write(plaintext)

    print(f"Fișier decriptat cu succes la: {decrypted_path}")
    return decrypted_path
