from flask import Flask, render_template, request
import numpy as np
import joblib

app = Flask(__name__)
model = joblib.load("model/heart_model.pkl")
model2 = joblib.load("model/heart_model_reduced.pkl")


@app.route('/index2')
def index2():
    return render_template('index2.html')


@app.route('/predict', methods=['POST'])
def predict2():
    # Extract features from form
    features = [float(request.form[feature]) for feature in [
        'cp', 'thalach', 'ca', 'oldpeak', 'thal', 'age']]

    # Reshape for prediction
    features_array = np.array(features).reshape(1, -1)

    # Make prediction
    prediction = model2.predict(features_array)[0]

    result = "has a high risk of heart disease." if prediction == 1 else "has a low risk of heart disease."

    return render_template('index2.html', prediction_text=f"The patient {result}")


@app.route('/index')
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
