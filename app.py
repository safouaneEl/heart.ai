import datetime
from collections import Counter
import base64
import io
import matplotlib.pyplot as plt
from flask import render_template, session, redirect
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
        patient_name = request.form['patient_name']
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

            result = "high" if prediction == 1 else "low"
            # Connexion DB
            doctor_email = session['user']
            cursor.execute("""INSERT INTO predictions (
                doctor_email, patient_name, age, sex, cp, trestbps, chol, fbs,
                restecg, thalach, exang, oldpeak, slope, ca, thal,
                prediction_result, probability
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                           (
                               doctor_email, patient_name, *features, result, prob
                           ))
            db.commit()
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


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/contact_page')
def contact_page():
    return render_template('contact_page.html')


@app.route('/contact_after_login')
def contact_after_login():
    return render_template('contact_after_login.html')


@app.route('/contact_login', methods=['POST'])
def contact_login():
    if 'user' not in session:
        return redirect('/login')  # ou /signup
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return "Tous les champs sont requis", 400

    try:
        cursor.execute("""
            INSERT INTO emails (name, email, message)
            VALUES (%s, %s, %s)
        """, (name, email, message))
        db.commit()
        return redirect(url_for('doctor_home'))  # Ou la page de succès
    except Exception as e:
        return f"Erreur lors de l'envoi du message: {str(e)}", 500


@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        return "Tous les champs sont requis", 400

    try:
        cursor.execute("""
            INSERT INTO emails (name, email, message)
            VALUES (%s, %s, %s)
        """, (name, email, message))
        db.commit()
        return redirect(url_for('index3'))  # Ou la page de succès
    except Exception as e:
        return f"Erreur lors de l'envoi du message: {str(e)}", 500


@app.route('/results')
def results():
    if 'user' not in session:
        return redirect('/login')  # ou /signup

    doctor = session['user']

    cursor.execute("""
        SELECT patient_name, age, sex, prediction_result, probability, prediction_date
        FROM predictions
        WHERE doctor_email = %s
        ORDER BY prediction_date DESC
    """, (doctor,))
    rows = cursor.fetchall()

    # Traduction
    label_map = {
        "high": "⚠️ High Risk",
        "low": "✅ Low Risk"
    }
    color_map = {
        "high": "red",
        "low": "green"
    }

    results = []
    count_risks = {"low": 0, "high": 0}
    sex_data = {"Homme": 0, "Femme": 0}
    age_data = []
    timeline_data = {"dates": [], "risks": []}

    for row in rows:
        patient_name, age, sex, pred, prob, date = row

        # Tableau principal
        results.append({
            "patient": patient_name,
            "age": age,
            "sex": "Homme" if sex == 1 else "Femme",
            "prediction_result": label_map.get(pred, "Inconnu"),
            "probability": f"{prob:.2f}%",
            "color": color_map.get(pred, "gray"),
            "prediction_date": date.strftime("%Y-%m-%d %H:%M")
        })

        # Données pour graphiques
        count_risks[pred] += 1
        sex_label = "Homme" if sex == 1 else "Femme"
        sex_data[sex_label] += 1
        age_data.append(age)

        # Pour timeline (par ex. dernier patient)
        timeline_data["dates"].append(date.strftime("%Y-%m-%d"))
        timeline_data["risks"].append(round(prob, 2))  # en pourcentage

    return render_template('results.html',
                           results=results,
                           risk_data=count_risks,
                           sex_data=sex_data,
                           age_data=age_data,
                           timeline_data=timeline_data)


# ----------------- tracage ------------------


def generate_pie_chart(data):
    fig, ax = plt.subplots()
    ax.pie(data.values(), labels=data.keys(),
           autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    return fig_to_base64(fig)


def generate_bar_chart(data_by_date):
    dates = list(data_by_date.keys())
    high_risks = [data_by_date[d]['High Risk'] for d in dates]
    low_risks = [data_by_date[d]['Low Risk'] for d in dates]

    fig, ax = plt.subplots()
    ax.bar(dates, low_risks, label='Low Risk', color='green')
    ax.bar(dates, high_risks, bottom=low_risks, label='High Risk', color='red')
    ax.set_ylabel('Nombre de prédictions')
    ax.set_xlabel('Date')
    ax.set_title('Prédictions par jour')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig_to_base64(fig)


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


if __name__ == '__main__':
    app.run(debug=True)
