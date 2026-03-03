import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import warnings
import pickle
import pandas as pd
import os
from convert import convertion
from train_model import train_model

warnings.filterwarnings('ignore')
from feature import FeatureExtraction

with open("newmodel.pkl", "rb") as f:
    model_data = pickle.load(f)
    if isinstance(model_data, dict):
        gbc = model_data['model']
        feature_names = model_data['feature_names']
    else:
        gbc = model_data
        feature_names = None

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "Phishing Detector API"})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    url = data.get('url')
    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    obj = FeatureExtraction(url)
    features_dict = obj.getFeaturesDict()

    # Select only the features the model was trained on, in the correct order
    if feature_names:
        x = pd.DataFrame([[features_dict[f] for f in feature_names]], columns=feature_names)
    else:
        x = np.array(list(features_dict.values())).reshape(1, -1)

    y_pred = gbc.predict(x)[0]

    result = convertion(url, int(y_pred))
    return jsonify({
        "url": result["url"],
        "prediction": result["prediction"],
        "safe": result["safe"]
    })

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json(force=True)
        url = data['url']
        actual_class = int(data['actual_class'])

        obj = FeatureExtraction(url)
        features_dict = obj.getFeaturesDict()
        features_dict['class'] = actual_class

        feedback_file = 'DataFiles/feedback.csv'
        df_new = pd.DataFrame([features_dict])

        if not os.path.exists(feedback_file):
            df_new.to_csv(feedback_file, index=False)
        else:
            df_new.to_csv(feedback_file, mode='a', header=False, index=False)

        return jsonify({"status": "success", "message": "Feedback saved."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    result = train_model()

    global gbc, feature_names
    with open("newmodel.pkl", "rb") as f:
        model_data = pickle.load(f)
        if isinstance(model_data, dict):
            gbc = model_data['model']
            feature_names = model_data['feature_names']
        else:
            gbc = model_data
            feature_names = None

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
