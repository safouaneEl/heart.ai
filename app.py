from flask import Flask, render_template, request
import numpy as np
import joblib

app = Flask(__name__)
model = joblib.load("model/heart_model.pkl")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
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
        return render_template('index.html', result=result, probability=f"{prob:.2f}%")
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
