import os
import base64
import paramiko
import socket
from flask import Flask

app = Flask(__name__)

SFTP_HOST = "transfer.resmed.com"
SFTP_PORT = 22
SFTP_USER = "ppcmy"

@app.route("/test_sftp")
def test_sftp_connection():
    try:
        key_b64 = os.environ.get("SFTP_PRIVATE_KEY_B64")
        if not key_b64:
            return "❌ SFTP_PRIVATE_KEY_B64 not found in environment!", 500

        key_path = "/tmp/temp_key.pem"
        with open(key_path, "wb") as f:
            f.write(base64.b64decode(key_b64))

        os.chmod(key_path, 0o600)  # make sure permission okay

        key = paramiko.RSAKey.from_private_key_file(key_path)

        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.close()
        transport.close()

        return "✅ SFTP connection succeeded!"
    except Exception as e:
        return f"❌ SFTP connection failed: {str(e)}", 500
