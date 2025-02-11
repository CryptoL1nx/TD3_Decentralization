import json
import numpy as np
from flask import Flask, request, jsonify
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Charger les données Iris
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Tester le modèle
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Accuracy du modèle : {accuracy:.2f}")

# Créer une application Flask
app = Flask(__name__)

@app.route('/predict', methods=['GET'])
def predict():
    """
    Endpoint GET /predict pour effectuer une prédiction
    Paramètres (via query string) : sepal_length, sepal_width, petal_length, petal_width
    """
    try:
        # Récupérer les paramètres de la requête
        sepal_length = float(request.args.get("sepal_length"))
        sepal_width = float(request.args.get("sepal_width"))
        petal_length = float(request.args.get("petal_length"))
        petal_width = float(request.args.get("petal_width"))
        features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])

        # Effectuer la prédiction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features).tolist()

        return jsonify({
            "prediction": int(prediction),
            "class_name": iris.target_names[prediction],
            "probability": probability
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
