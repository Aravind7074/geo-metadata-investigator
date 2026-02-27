import os
from google.cloud import vision

# 1. Point to the key file you just renamed
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def test_connection():
    try:
        client = vision.ImageAnnotatorClient()
        # This sends a 'dry run' request to Google
        print("✅ Success: Google Vision client initialized.")
        print("Your MSI is now connected to the Cloud.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()