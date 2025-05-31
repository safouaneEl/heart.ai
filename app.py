from flask import Flask, render_template, request, redirect, session, url_for
import os
import numpy as np
import joblib
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


# Establish a connection to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2025MYSQLs@f",
    database="heart_ai"
)
cursor = db.cursor()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

model = joblib.load("model/heart_model.pkl")
model2 = joblib.load("model/heart_model_reduced.pkl")


@app.route('/index3')
def index3():
    return render_template('index3.html')


@app.route('/index2', methods=['GET', 'POST'])
def index2():
    if 'user' not in session:
        return redirect('/signup')  # ou vers '/login'

    if request.method == 'POST':
        try:
            features = [
                float(request.form['age']),
                float(request.form['sex']),
                float(request.form['cp']),
                float(request.form['trestbps']),
                float(request.form['chol']),
                float(request.form['fbs']),
                float(request.form['restecg']),
                float(request.form['thalach']),
                float(request.form['exang']),
                float(request.form['oldpeak']),
                float(request.form['slope']),
                float(request.form['ca']),
                float(request.form['thal'])
            ]
            input_data = np.array([features])
            prediction = model.predict(input_data)[0]
            prob = model.predict_proba(input_data)[0][1] * 100

            result = "⚠️ High Risk" if prediction == 1 else "✅ Low Risk"
            return render_template('index2.html', result=result, probability=f"{prob:.2f}%")
        except Exception as e:
            return str(e)
    else:
        # GET : afficher la page avec le formulaire vide
        return render_template('index2.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/success')
def success():
    return "Signup successful! You can now log in."


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        birthdate = request.form['birthdate']
        specialite = request.form['specialite']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match!"

        # You should hash the password before storing it (see note below)
        hashed_password = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO signup (fullname, email,birthdate, specialite,password)
            VALUES (%s, %s, %s,%s,%s)
        """, (fullname, email, birthdate, specialite, hashed_password))
        db.commit()
        return redirect('/doctor_home')
    return render_template('signup.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Fetch user by email
    cursor.execute("SELECT * FROM signup WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        # assuming password is in the 6th column (index 5)
        stored_hashed_password = user[5]
        if check_password_hash(stored_hashed_password, password):
            session['user'] = user[1]  # store fullname or email as needed
            return redirect('/doctor_home')  # or any page you want
        else:
            return "Incorrect password"
    else:
        return "Email not found"


@app.route('/logout')
def logout():
    session.clear()  # Supprime toutes les données de session
    # Redirige vers la page d'accueil (non connectée)
    return redirect(url_for('index3'))


@app.route('/doctor_home')
def doctor_home():
    if 'user' not in session:
        return redirect('/signup')  # ou vers '/login' si tu en as un
    return render_template('doctor_home.html', user=session['user'])


if __name__ == '__main__':
    app.run(debug=True)
