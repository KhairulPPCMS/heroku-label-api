from flask import Flask, request, jsonify

app = Flask(__name__)

# Dummy sFTP check function (nanti kita ganti dengan logic sebenar)
def check_job_in_sftp(job_no):
    return job_no == "JOB12345"  # tukar ni nanti ikut real sFTP

# Root route untuk elak 404 bila access /
@app.route('/')
def home():
    return "Hello dari Render!"

# Main API untuk check Job No
@app

