from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector

from werkzeug.security import generate_password_hash, check_password_hash

from utils.sms_predict import predict_sms
from utils.email_predict import predict_email
from utils.phishing_predict import predict_url

from dotenv import load_dotenv
import os

# ==========================================
# LOAD ENV
# ==========================================
load_dotenv()

# ==========================================
# APP SETUP
# ==========================================
app = Flask(__name__)
app.secret_key = "cybershield_secret_key"

# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="NayaPassword123",
        database="cybershieldai"
    )

# ==========================================
# HOME PAGE
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')

# ==========================================
# REGISTER
# ==========================================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """, (username, email, password))

        db.commit()
        cursor.close()
        db.close()

        return redirect('/login')

    return render_template('register.html')

# ==========================================
# LOGIN
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT id, username, password_hash
            FROM users
            WHERE email=%s
        """, (email,))

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user[2], password):

            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect('/dashboard')

        return "Invalid Credentials"

    return render_template('login.html')

# ==========================================
# LOGOUT
# ==========================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==========================================
# DASHBOARD
# ==========================================
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template('dashboard.html', username=session['username'])

# ==========================================
# SMS DETECTION
# ==========================================
@app.route('/sms', methods=['GET', 'POST'])
def sms():

    if 'user_id' not in session:
        return redirect('/login')

    result = ""

    if request.method == 'POST':

        message = request.form.get('sms')

        if message and message.strip():
            result = predict_sms(message)

    return render_template('sms.html', result=result)

# ==========================================
# EMAIL DETECTION
# ==========================================
@app.route('/email', methods=['GET', 'POST'])
def email():

    if 'user_id' not in session:
        return redirect('/login')

    result = ""

    if request.method == 'POST':

        message = request.form['message']
        result = predict_email(message)

    return render_template('email.html', result=result)

# ==========================================
# PHISHING DETECTION
# ==========================================
@app.route('/phishing', methods=['GET', 'POST'])
def phishing():

    if 'user_id' not in session:
        return redirect('/login')

    result = ""

    if request.method == 'POST':

        url = request.form.get('url', '').strip()

        if url:
            result = predict_url(url)

    return render_template('phishing.html', result=result)

# ==========================================
# FEEDBACK
# ==========================================
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        message = request.form['message']

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO feedback (username, message)
            VALUES (%s, %s)
        """, (session['username'], message))

        db.commit()
        cursor.close()
        db.close()

        return "Feedback Submitted"

    return render_template('feedback.html')

# ==========================================
# ADMIN PANEL
# ==========================================
@app.route('/admin')
def admin():

    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM history")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        'admin.html',
        total_users=total_users,
        total_predictions=total_predictions,
        total_feedback=total_feedback,
        users=users
    )

# ==========================================
# RUN APP
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)