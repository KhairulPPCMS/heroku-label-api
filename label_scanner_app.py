import os
import paramiko
from flask import Flask

app = Flask(__name__)

SFTP_HOST = "transfer.resmed.com"
SFTP_PORT = 22
SFTP_USER = "PPC_MY_PRD"
KEY_FILE_PATH = "/etc/secrets/sftp_key.pem"

@app.route("/test_sftp")
def test_sftp_connection():
    try:
        # BUANG chmod sini sebab /etc/secrets read-only
        key = paramiko.RSAKey.from_private_key_file(KEY_FILE_PATH)

        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Example action: list files at remote root
        sftp.chdir("/PPC_MY_PRD")
        files = sftp.listdir()

        sftp.close()
        transport.close()

        return f"✅ SFTP connected! Files: {files}"
    except Exception as e:
        return f"❌ SFTP failed: {str(e)}", 500
