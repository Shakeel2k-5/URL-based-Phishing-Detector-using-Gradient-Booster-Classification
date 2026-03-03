import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

# Features that are broken/stubbed at prediction time and cause misclassification:
# - google_index: encoding inverted vs feature extractor (dataset 1=phishing, extractor 1=indexed)
# - page_rank: always returns 0, and page_rank=0 is 96% phishing in training data
# - web_traffic: always returns 0, and web_traffic=0 is 81% phishing in training data
# - dns_record: nearly all 0 in dataset regardless of class (useless)
# - ratio_intErrors, ratio_extErrors: hardcoded to 0 in feature extractor
DROP_FEATURES = [
    'google_index', 'page_rank', 'web_traffic',
    'dns_record', 'ratio_intErrors', 'ratio_extErrors',
]


def train_model():
    df = pd.read_csv('dataset_phishing.csv')

    # Encode target
    df['status'] = df['status'].map({'legitimate': 1, 'phishing': -1})

    # Separate features and target, dropping broken features
    feature_cols = [c for c in df.columns if c not in ('url', 'status') and c not in DROP_FEATURES]
    X = df[feature_cols]
    y = df['status']

    # Load feedback if available
    feedback_file = 'DataFiles/feedback.csv'
    if os.path.exists(feedback_file):
        fb = pd.read_csv(feedback_file)
        if set(feature_cols + ['class']).issubset(fb.columns):
            fb = fb.rename(columns={'class': 'status'})
            X = pd.concat([X, fb[feature_cols]], ignore_index=True)
            y = pd.concat([y, fb['status']], ignore_index=True)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train Gradient Boosting (better generalization than Random Forest)
    model = GradientBoostingClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.1,
        min_samples_split=10,
        min_samples_leaf=4,
        subsample=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['Phishing', 'Safe'])
    print(f'Accuracy: {accuracy:.4f}')
    print(report)

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f'Cross-val accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})')

    # Save model and feature names
    with open('newmodel.pkl', 'wb') as f:
        pickle.dump({'model': model, 'feature_names': feature_cols}, f)

    return {
        "status": "success",
        "message": "Model retrained successfully",
        "samples": len(X),
        "accuracy": round(accuracy, 4)
    }


if __name__ == "__main__":
    result = train_model()
    print(result)
