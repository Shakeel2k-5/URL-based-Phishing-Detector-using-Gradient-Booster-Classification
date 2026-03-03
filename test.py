import requests

BASE_URL = "http://127.0.0.1:5001"

def predict(url):
    response = requests.post(f"{BASE_URL}/predict", json={"url": url})
    data = response.json()
    print(f"\nURL: {data['url']}")
    print(f"Prediction: {data['prediction']}")
    print(f"Safe: {data['safe']}")
    return data

def retrain():
    response = requests.post(f"{BASE_URL}/retrain")
    data = response.json()
    print(f"\nRetrain Status: {data['status']}")
    print(f"Message: {data['message']}")
    print(f"Samples: {data['samples']}")

if __name__ == "__main__":
    url = input("Enter URL: ")
    result = predict(url)

    if not result["safe"]:
        print("\n[!] This website is NOT safe. Submitting as phishing for retraining...")
        requests.post(f"{BASE_URL}/feedback", json={"url": url, "actual_class": -1})
    else:
        print("\n[+] This website is safe.")

    retrain()
