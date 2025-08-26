from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from io import StringIO
import random
import string

app = Flask(__name__)
CORS(app)

# Simple user authentication; for production, use a database
users = {
    "admin": "adminpassword"
}

attendance_data = {}  # {date: {regno: {"name": name, "status": status}}}

EMAIL_ADDRESS = "vinaypydi85@gmail.com"
EMAIL_PASSWORD = "pxbntsohbnbojhtw"  # Use your app password securely

@app.route('/')
def home():
    return render_template('attendance.html')

@app.route('/reset-password')
def reset_password():
    # You can create a proper reset page/template if you wish!
    return "<h2>Password Reset Page - Feature under construction.</h2>"

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in users and users[username] == password:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid username or password"})

def generate_temp_password(length=8):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    username = data.get('username')
    if username in users:
        try:
            temp_password = generate_temp_password()
            # Update user's password to temporary password
            users[username] = temp_password
            send_temp_password_email(temp_password)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": "Failed to send reset email"})
    return jsonify({"success": False, "error": "Username not found"})

def send_temp_password_email(temp_password):
    msg = MIMEText(f'Your temporary password is: {temp_password}\nPlease use this password to login and change it immediately.')
    msg['Subject'] = 'Your Temporary Password'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS  # Change to recipient email in production
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

@app.route('/api/save', methods=['POST'])
def save_attendance():
    data = request.json
    date = data.get('date')
    attendance = data.get('attendance')
    if not date or not attendance:
        return jsonify({"success": False, "error": "Date or attendance missing"})
    attendance_data[date] = attendance
    return jsonify({"success": True})

@app.route('/api/check')
def check_attendance():
    regno = request.args.get('regno')
    date = request.args.get('date')
    if not regno or not date:
        return jsonify({"status": "Absent"})
    status = attendance_data.get(date, {}).get(regno, {}).get('status', "Absent")
    return jsonify({"status": status})

@app.route('/api/export_absentees/')
def export_absentees():
    date = request.args.get('date')
    if not date or date not in attendance_data:
        return "No attendance data found for this date", 404
    absentees = []
    for regno, info in attendance_data[date].items():
        if info.get('status') != 'Present':
            absentees.append(f"{regno} - {info.get('name')} - {info.get('status')}")
    absentees_str = "\n".join(absentees)
    return send_file(
        StringIO(absentees_str),
        mimetype="text/plain",
        as_attachment=True,
        download_name=f"absentees-{date}.txt"
    )

if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
