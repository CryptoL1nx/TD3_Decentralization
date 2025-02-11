import json
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize a JSON database to track model balances and weights
DATABASE_FILE = "model_data.json"

def initialize_database():
    """Initializes the JSON database if it doesn't already exist."""
    try:
        with open(DATABASE_FILE, 'r') as file:
            json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {
            "models": {}  # Format: {"model_id": {"balance": 1000, "weight": 1.0, "accuracy": []}}
        }
        with open(DATABASE_FILE, 'w') as file:
            json.dump(data, file, indent=4)

def read_database():
    """Reads data from the JSON database."""
    with open(DATABASE_FILE, 'r') as file:
        return json.load(file)

def write_database(data):
    """Writes data to the JSON database."""
    with open(DATABASE_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize the database
initialize_database()

@app.route('/register', methods=['POST'])
def register_model():
    """Registers a new model with an initial balance."""
    data = request.json
    model_id = data.get("model_id")
    initial_balance = 1000  # Default deposit

    if not model_id:
        return jsonify({"error": "model_id is required"}), 400

    db = read_database()
    if model_id in db["models"]:
        return jsonify({"error": "Model already registered"}), 400

    db["models"][model_id] = {"balance": initial_balance, "weight": 1.0, "accuracy": []}
    write_database(db)

    return jsonify({"message": f"Model {model_id} registered successfully with balance {initial_balance}"})

@app.route('/predict', methods=['POST'])
def predict():
    """Accepts predictions from a model and evaluates accuracy."""
    data = request.json
    model_id = data.get("model_id")
    prediction = data.get("prediction")
    actual = data.get("actual")

    if not model_id or prediction is None or actual is None:
        return jsonify({"error": "model_id, prediction, and actual are required"}), 400

    db = read_database()
    model_data = db["models"].get(model_id)
    if not model_data:
        return jsonify({"error": "Model not found"}), 404

    # Update accuracy and adjust balance based on performance
    accuracy = 1.0 if prediction == actual else 0.0
    model_data["accuracy"].append(accuracy)

    if len(model_data["accuracy"]) > 10:  # Limit accuracy history to 10 predictions
        model_data["accuracy"].pop(0)

    avg_accuracy = sum(model_data["accuracy"]) / len(model_data["accuracy"])
    model_data["weight"] = avg_accuracy  # Adjust weight based on accuracy

    # Slashing for low accuracy
    if avg_accuracy < 0.5:  # Arbitrary threshold for slashing
        penalty = 100  # Arbitrary penalty amount
        model_data["balance"] -= penalty
        if model_data["balance"] < 0:
            model_data["balance"] = 0

    db["models"][model_id] = model_data
    write_database(db)

    return jsonify({
        "message": "Prediction recorded",
        "model_id": model_id,
        "accuracy": accuracy,
        "average_accuracy": avg_accuracy,
        "balance": model_data["balance"],
        "weight": model_data["weight"]
    })

@app.route('/status', methods=['GET'])
def model_status():
    """Returns the status of all registered models."""
    db = read_database()
    return jsonify(db["models"])

@app.route('/slash', methods=['POST'])
def slash_model():
    """Manually slashes a model's balance for malicious behavior."""
    data = request.json
    model_id = data.get("model_id")
    penalty = data.get("penalty", 0)

    if not model_id or penalty <= 0:
        return jsonify({"error": "model_id and positive penalty are required"}), 400

    db = read_database()
    model_data = db["models"].get(model_id)
    if not model_data:
        return jsonify({"error": "Model not found"}), 404

    model_data["balance"] -= penalty
    if model_data["balance"] < 0:
        model_data["balance"] = 0

    db["models"][model_id] = model_data
    write_database(db)

    return jsonify({
        "message": f"Model {model_id} slashed by {penalty}",
        "new_balance": model_data["balance"]
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
