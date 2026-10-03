import os
import uuid
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from dotenv import load_dotenv

from db import build_db_data, store_file

load_dotenv()


def create_folder_key(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    return True


def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys(private_key, public_key, key_id: str, dir_path: Path):
    create_folder_key(dir_path)

    # Preluăm parola și o transformăm în bytes
    password = os.getenv("PASSWORD", "parolaimplicita").encode("utf-8")

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_path = dir_path / f"{key_id}_private.pem"
    public_path = dir_path / f"{key_id}_public.pem"

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)
    print(f"Cheile pentru {key_id} au fost salvate.")


def encrypt_file(path: Path, public_key, encrypted_path: Path):
    with open(path, "rb") as file:
        file_contents = file.read()

        ciphertext = public_key.encrypt(
            file_contents,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        encrypted_path.parent.mkdir(parents=True, exist_ok=True)
        with open(encrypted_path, "wb") as enc_file:
            enc_file.write(ciphertext)


def encryption(file_path: Path):
    private_key, public_key = generate_keys()

    key_id_str = str(uuid.uuid4())

    encrypted_folder = Path("../encrypted_files")
    encrypted_file_path = encrypted_folder / f"enc_{file_path.name}.bin"

    encrypt_file(file_path, public_key, encrypted_file_path)

    save_keys(
        private_key=private_key,
        public_key=public_key,
        key_id=key_id_str,
        dir_path=Path("../key_dir"),
    )

    db_record = build_db_data(
        original_filename=file_path.name,
        encryption_method="RSA-2048",
        encrypted_file_path=str(encrypted_file_path),
        key_id=key_id_str,
    )

    store_file([db_record])
    print("Fișierul a fost criptat și adăugat în baza de date cu succes!")
