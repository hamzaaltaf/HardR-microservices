from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def encrypt(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def validate_password(password_hash, password):
    val = bcrypt.check_password_hash(password_hash, password)
    print(f"Password Hash: {password_hash}")
    print(f"Password Provided: {password}")
    print(f"Validation Result: {val}")
    return val
