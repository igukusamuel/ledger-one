import hashlib

# Hardcoded demo users (replace with DB later)
USERS = {
    "owner": {"password": "owner123", "role": "Owner"},
    "cashier": {"password": "cash123", "role": "Cashier"},
    "manager": {"password": "manager123", "role": "Manager"},
}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username, password):
    user = USERS.get(username)
    if not user:
        return None

    if user["password"] == password:
        return user["role"]

    return None
