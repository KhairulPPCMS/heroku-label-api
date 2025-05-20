from flask import Flask, request, jsonify
import paramiko
import os
from io import StringIO

app = Flask(__name__)

# --- SFTP Config ---
SFTP_HOST = "transfer.resmed.com"
SFTP_PORT = 22
SFTP_USERNAME = "PPC_MY_PRD"
PRIVATE_KEY_CONTENT = os.getenv("PRIVATE_KEY_CONTENT")
remote_root = "/PPC_MY_PRD"

def connect_sftp():
    keyfile = StringIO(PRIVATE_KEY_CONTENT)
    private_key = paramiko.RSAKey.from_private_key(keyfile)

    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

@app.route("/check_job", methods=["POST"])
def check_job():
    data = request.get_json()
    job_no = data.get("job_no")
    if not job_no:
        return jsonify({"status": "error", "message": "Missing job number"}), 400

    if check_job_in_sftp(job_no):
        return jsonify({"status": "found", "message": f"Job {job_no} found"}), 200
    else:
        return jsonify({"status": "not_found", "message": f"Job {job_no} not found"}), 404

@app.route("/test_sftp", methods=["GET"])
def test_sftp_connection():
    try:
        sftp, transport = connect_sftp()
        sftp.close()
        transport.close()
        return jsonify({"status": "success", "message": "SFTP connection OK"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
