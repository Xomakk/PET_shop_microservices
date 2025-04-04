from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Generates a secure hash from a plain text password using configured password context.

    Args:
        password: Plain text password to be hashed

    Returns:
        str: Secure hashed version of the password suitable for storage

    Example:
        >>> hashed = get_password_hash("mysecret")
        >>> isinstance(hashed, str)
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored hash.

    Args:
        plain_password: Password to verify in plain text
        hashed_password: Previously hashed password to compare against

    Returns:
        bool: True if password matches the hash, False otherwise

    Example:
        >>> hashed = get_password_hash("mysecret")
        >>> verify_password("mysecret", hashed)
        True
        >>> verify_password("wrongpass", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)
