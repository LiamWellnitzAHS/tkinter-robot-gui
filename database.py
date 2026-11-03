import sqlite3
import hashlib
import os
from cryptography.fernet import Fernet

# File paths for the database and encryption key
db_file = "database_temp.db"
encrypted_db_file = "database.db"
key_file = "key.key"

# Loads the encryption key from file or generates one if it doesn't exist
def load_key():
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            return file.read()
    key = Fernet.generate_key()
    with open(key_file, "wb") as file:
        file.write(key)
    return key

# Decrypts the main encrypted database into a temporary database
def decrypt_db():
    if os.path.exists(encrypted_db_file):
        fernet = Fernet(load_key())
        with open(encrypted_db_file, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        with open(db_file, "wb") as file:
            file.write(decrypted_data)

# Encrypts the temporary database into the encrypted database file and deletes the temp database file
def encrypt_db():
    if os.path.exists(db_file):
        fernet = Fernet(load_key())
        with open(db_file, "rb") as file:
            data = file.read()
        encrypted_data = fernet.encrypt(data)
        with open(encrypted_db_file, "wb") as file:
            file.write(encrypted_data)
        os.remove(db_file)

# Starts the database and creates the users table if it doesn't exist
def start_db():
    decrypt_db()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(
    """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    encrypt_db()

# Hashes a password using sha-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registers a new user with a hashed password in the database
def register_user(username, password):
    decrypt_db()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        conn.close()
        encrypt_db()
    return success

# Verifies user information against the password hash
def verify_user(username, password):
    decrypt_db()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    encrypt_db()
    
    if row and row[0] == hash_password(password):
        return True
    return False
