from flask import Flask, request, jsonify

app = Flask(__name__)

# Dummy function untuk simulate semakan Job No dalam sFTP
def check_job_in_sftp(job_no):
    # Ganti logic sebenar nanti
    return job_no == "JOB12345"

# Root route untuk elak 404 bila buka /
@app.route('/')
def home():
    return "Hello dari Render!"

# API endpoint untuk check Job No
@app.route('/check_job', methods=['POST'])
def check_job():
    data = request.get_json()

    if not data or 'job_no' not in data:
        return jsonify({"error": "Missing job_no"}), 400

    job_no = data['job_no']

    if check_job_in_sftp(job_no):
        return jsonify({"job_no": job_no, "status": "Valid Job No"})
    
    return jsonify({"job_no": job_no, "status": "Job No not found"})

# Wajib untuk local test, tak effect kat Render
if __name__ == '__main__':
    app.run(debug=True)

