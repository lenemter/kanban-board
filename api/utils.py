import bcrypt


HASH_ALGORITHM = "HS256"

secrets_cache: dict[str, str] = dict()


def read_secret(secret_name: str) -> str | None:
    if secret_name in secrets_cache:
        return secrets_cache[secret_name]

    try:
        with open(f"secrets/{secret_name}") as file:
            secret_content = file.read()
            secrets_cache[secret_name] = secret_content

            return secret_content
    except OSError:
        print("File not found")
        return None


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
