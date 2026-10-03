from pathlib import Path


def delete_encrypted_file(encrypted_file_path: str):
    path = Path(encrypted_file_path)
    path.unlink(missing_ok=True)
    print(f"Fișierul criptat {path.name} a fost șters (dacă exista)!")


def delete_key(key_id: str):
    key_dir = Path("../key_dir")
    private_path = key_dir / f"{key_id}_private.pem"
    public_path = key_dir / f"{key_id}_public.pem"

    private_path.unlink(missing_ok=True)
    public_path.unlink(missing_ok=True)
    print(f"Cheile pentru {key_id} au fost șterse.")


def delete_entry(encrypted_file_path: str, key_id: str):
    delete_encrypted_file(encrypted_file_path)
    delete_key(key_id)
