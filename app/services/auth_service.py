import hashlib
import hmac
import re
import secrets

from sqlalchemy import text
from sqlalchemy.orm import Session


PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:

    salt = secrets.token_bytes(32)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )

    return (
        f"pbkdf2_sha256$"
        f"{PASSWORD_ITERATIONS}$"
        f"{salt.hex()}$"
        f"{password_hash.hex()}"
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:

    try:

        algorithm, iterations, salt_hex, hash_hex = (
            stored_hash.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)

        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except (ValueError, TypeError):

        return False


def validate_email(email: str) -> bool:

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(
            pattern,
            email,
        )
    )


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
):

    name = name.strip()
    email = email.strip().lower()

    if not name:
        raise ValueError(
            "Name is required."
        )

    if not validate_email(email):
        raise ValueError(
            "Enter a valid email address."
        )

    if len(password) < 6:
        raise ValueError(
            "Password must contain at least 6 characters."
        )

    existing = db.execute(
        text(
            """
            SELECT id
            FROM users
            WHERE email = :email
            """
        ),
        {
            "email": email
        },
    ).fetchone()

    if existing:

        raise ValueError(
            "An account with this email already exists."
        )

    password_hash = hash_password(password)

    result = db.execute(
        text(
            """
            INSERT INTO users (
                name,
                email,
                password_hash
            )
            VALUES (
                :name,
                :email,
                :password_hash
            )
            RETURNING
                id,
                name,
                email,
                created_at
            """
        ),
        {
            "name": name,
            "email": email,
            "password_hash": password_hash,
        },
    )

    user = result.fetchone()

    db.commit()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at,
    }


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):

    email = email.strip().lower()

    user = db.execute(
        text(
            """
            SELECT
                id,
                name,
                email,
                password_hash,
                created_at
            FROM users
            WHERE email = :email
            """
        ),
        {
            "email": email
        },
    ).fetchone()

    if not user:

        raise ValueError(
            "Invalid email or password."
        )

    if not verify_password(
        password,
        user.password_hash,
    ):

        raise ValueError(
            "Invalid email or password."
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at,
    }