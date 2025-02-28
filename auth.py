import base64
import secrets
import mysql.connector
import bcrypt
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Đọc private key từ file
with open("/.ssh/api_key", "rb") as key_file:
    private_key = serialization.load_ssh_private_key(
        key_file.read(),
        password=None,  # Không có passphrase
        backend=default_backend()
    )

# Đọc public key từ file
with open("/.ssh/api_key.pub", "rb") as key_file:
    public_key = serialization.load_ssh_public_key(
        key_file.read(),
        backend=default_backend()
    )

cnx = mysql.connector.connect(
    host="api_hubs_mysql",
    user="api_hubs",
    port=3306,
    password="api_hubs_pass",
    database="api_hubs_mysql"
)

cursor = cnx.cursor()
cursor.execute(
    "create TABLE IF not EXISTS account_api_key ( account_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,account_name VARCHAR(255) NOT NULL,account_password VARCHAR(255) NOT NULL,api_key LONGTEXT);"
)

def create_account(account_name, account_password):
    salt = bcrypt.gensalt()
    password_encode = account_password.encode('utf-8')
    hash_password = bcrypt.hashpw(password_encode, salt)
    if cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("INSERT INTO account_api_key (account_name, account_password) VALUES (%s, %s)", (account_name, hash_password))
            cnx.commit()
        return True
    else:
        return False

# Hàm để kiểm tra tài khoản
def check_account(account_name, account_password):

    if not cnx.is_connected():
        return False

    with cnx.cursor() as cursor:
        cursor.execute("SELECT account_password FROM account_api_key WHERE account_name = %s",(account_name,))
        result = cursor.fetchone()
        print(result)
        if result is not None:
            if bcrypt.checkpw(account_password.encode('utf-8'), result[0].encode('utf-8')):
                return True
            else: return False
        else: return False

# Hàm để tạo ra api key
def generate_api_key(account_name, account_password):
    # Check account
    if not check_account(account_name, account_password):
        return "user not found"
    # Generate key
    api_keys = secrets.token_urlsafe(16)
    # Sign apikey and generate signature
    signature = sign_message(api_keys)
    if not cnx.is_connected():
        return 'not connected'
    with cnx.cursor() as cursor:
        cursor.execute("UPDATE account_api_key SET api_key = %s WHERE account_name = %s", (signature, account_name))
        cnx.commit()
    return api_keys

# Hàm ký message
def sign_message(message: str):
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

# Hàm xác minh message
import base64

# Hàm xác minh message
def verify_message(message: str, account_name: str):
    try:
        with cnx.cursor() as cursor:
            cursor.execute("SELECT api_key FROM account_api_key WHERE account_name = %s", (account_name,))
            signature = cursor.fetchone()

            if not signature:
                return False

            signature_str = signature[0]
            if isinstance(signature_str, bytes):
                signature_str = signature_str.decode()

            signature_bytes = base64.b64decode(signature_str)

            public_key.verify(
                signature_bytes,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
    except Exception as e:
        print("Verification failed:", e)
        return False

# Ví dụ sử dụng


#is_valid = verify_message(message, signature)
#print("Is valid:", is_valid)