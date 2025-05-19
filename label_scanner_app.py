import os
from flask import Flask, request, jsonify
import paramiko

app = Flask(__name__)

# --- SFTP Config ---
SFTP_HOST = "transfer.resmed.com"
SFTP_PORT = 22
SFTP_USERNAME = "PPC_MY_PRD"
SFTP_REMOTE_ROOT = "/PPC_MY_PRD"

# Path temporary untuk simpan private key
PRIVATE_KEY_PATH = "/tmp/private_key.pem"

def prepare_private_key():
    private_key_content = os.getenv("PRIVATE_KEY_CONTENT")
    if not private_key_content:
        raise Exception("Missing PRIVATE_KEY_CONTENT environment variable")

    # Write private key content to temporary file
    with open(PRIVATE_KEY_PATH, "w") as f:
        f.write(private_key_content)

    os.chmod(PRIVATE_KEY_PATH, 0o600)  # Permission read/write owner only

def connect_sftp():
    prepare_private_key()
    key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

def check_job_in_sftp(job_no):
    try:
        sftp, transport = connect_sftp()
        files = sftp.listdir(SFTP_REMOTE_ROOT)
        sftp.close()
        transport.close()
    except Exception as e:
        print("SFTP connection error:", e)
        return False

    # Simple check: job_no must be substring of any filename in remote folder
    for filename in files:
        if job_no in filename:
            return True
    return False

@app.route("/")
def home():
    return "Flask app for job number validation"

@app.route("/check_job", methods=["POST"])
def check_job():
    data = request.get_json()
    if not data or "job_no" not in data:
        return jsonify({"error": "Missing job_no"}), 400

    job_no = data["job_no"]

    if check_job_in_sftp(job_no):
        return jsonify({"job_no": job_no, "status": "Valid Job No"})
    else:
        return jsonify({"job_no": job_no, "status": "Job No not found"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

