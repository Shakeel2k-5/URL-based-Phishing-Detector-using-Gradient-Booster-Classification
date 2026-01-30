import numpy as np
from flask import Flask, request, jsonify
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
    features = obj.getFeaturesList()
    x = np.array(features).reshape(1, -1)
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
        features = obj.getFeaturesList()

        row = features + [actual_class]
        cols = ['UsingIP','LongURL','ShortURL','Symbol@','Redirecting//','PrefixSuffix-','SubDomains','HTTPS','DomainRegLen','Favicon','NonStdPort','HTTPSDomainURL','RequestURL','AnchorURL','LinksInScriptTags','ServerFormHandler','InfoEmail','AbnormalURL','WebsiteForwarding','StatusBarCust','DisableRightClick','UsingPopupWindow','IframeRedirection','AgeofDomain','DNSRecording','WebsiteTraffic','PageRank','GoogleIndex','LinksPointingToPage','StatsReport','class']

        feedback_file = 'DataFiles/feedback.csv'
        df_new = pd.DataFrame([row], columns=cols)

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
