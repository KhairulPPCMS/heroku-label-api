from flask import Flask, request, jsonify
import paramiko
import re
import os
import io

app = Flask(__name__)

# --- SFTP Configuration (from Render Environment Variable) ---
hostname = "transfer.resmed.com"
username = "PPC_MY_PRD"
remote_root = "/PPC_MY_PRD"

# Load private key from environment variable
private_key_content = os.environ.get("PRIVATE_KEY_CONTENT")
if not private_key_content:
    raise Exception("❌ PRIVATE_KEY_CONTENT not set!")

private_key = paramiko.RSAKey.from_private_key(io.StringIO(private_key_content))

def get_all_job_orders_from_sftp():
    job_orders_found = set()
    try:
        transport = paramiko.Transport((hostname, 22))
        transport.connect(username=username, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        def list_files(path):
            for item in sftp.listdir_attr(path):
                full_path = os.path.join(path, item.filename).replace("\\", "/")
                if paramiko.SFTPAttributes.S_ISDIR(item.st_mode):
                    list_files(full_path)
                elif item.filename.lower().endswith(".xlsx"):
                    match = re.search(r"(PPC-JO-[A-Z]*\d+)", item.filename)
                    if match:
                        job_orders_found.add(match.group(1))

        list_files(remote_root)
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"❌ SFTP Error: {e}")
    return job_orders_found

@app.route("/check-job", methods=["POST"])
def check_job():
    data = request.json
    job_number = data.get("job_number", "").strip().upper()

    if not job_number.startswith("PPC-JO-"):
        return jsonify({"status": "error", "message": "Invalid job number format"}), 400

    job_orders = get_all_job_orders_from_sftp()
    if job_number in job_orders:
        return jsonify({"status": "found", "job_number": job_number})
    else:
        return jsonify({"status": "not found", "job_number": job_number})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

