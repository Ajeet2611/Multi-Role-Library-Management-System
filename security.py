import bcrypt


def hash_password(password: str) -> str:
    """
    Plain password ko secure hash me convert karta hai
    """
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()


def check_password(password: str, hashed_password: str) -> bool:
    """
    Login ke time password verify karta hai
    """
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
