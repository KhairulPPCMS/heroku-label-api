from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock function untuk semak job number
def check_job_in_sftp(job_no):
    # Untuk test, kita anggap "JOB12345" ada, lain-lain takde
    if job_no == "JOB12345":
        return True
    else:
        return False

@app.route('/')
def home():
    return "Hello dari Render.com!"

@app.route('/check_job', methods=['POST'])
def check_job():
    data = request.get_json()
    if not data or 'job_no' not in data:
        return jsonify({"error": "Missing job_no in request"}), 400

    job_no = data['job_no']
    found = check_job_in_sftp(job_no)

    if found:
        return jsonify({"job_no": job_no, "status": "Valid Job No"})
    else:
        return jsonify({"job_no": job_no, "status": "Job No not found"})

if __name__ == '__main__':
    app.run(debug=True)

