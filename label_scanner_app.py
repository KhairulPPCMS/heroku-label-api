from flask import Flask
import paramiko
import os
import tempfile
import socket
import base64

app = Flask(__name__)

# Config
SFTP_HOST = "transfer.resmed.com"
SFTP_PORT = 22
SFTP_USERNAME = "ppcmy"
PRIVATE_KEY_B64 = os.getenv("SFTP_PRIVATE_KEY_B64")  # from Render

def connect_sftp():
    # Decode private key dari base64
    private_key_data = base64.b64decode(PRIVATE_KEY_B64)

    # Simpan sementara dalam file
    with tempfile.NamedTemporaryFile(delete=False) as key_file:
        key_file.write(private_key_data)
        key_file_path = key_file.name

    # Load private key dan connect
    private_key = paramiko.RSAKey.from_private_key_file(key_file_path)
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

@app.route("/")
def home():
    return "Flask API is running."

@app.route("/test_socket")
def test_socket():
    try:
        sock = socket.create_connection((SFTP_HOST, SFTP_PORT), timeout=5)
        sock.close()
        return "✅ Socket connection to port 22 succeeded!"
    except Exception as e:
        return f"❌ Socket connection failed: {e}"

@app.route("/test_sftp")
def test_sftp_connection():
    try:
        sftp, transport = connect_sftp()
        sftp.close()
        transport.close()
        return "✅ SFTP connection succeeded!"
    except Exception as e:
        return f"❌ SFTP connection failed: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
