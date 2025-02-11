import requests

# Étape 1 : Tester l'API /predict de model_api.py
response = requests.get(
    "http://localhost:5001/predict",
    params={
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
)

if response.status_code == 200:
    prediction_data = response.json()
    print(f"Prediction Response: {prediction_data}")

    # Étape 2 : Envoyer la prédiction au serveur decentralized_consensus.py
    model_id = "logistic_model"
    actual_label = 0  # Remplacez par la vraie classe selon le dataset
    consensus_response = requests.post(
        "http://localhost:5000/predict",
        json={
            "model_id": model_id,
            "prediction": prediction_data["prediction"],
            "actual": actual_label
        }
    )

    if consensus_response.status_code == 200:
        print(f"Consensus Response: {consensus_response.json()}")
    else:
        print(f"Error in consensus system: {consensus_response.text}")
else:
    print(f"Error in model API: {response.text}")
