from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv
from stockbuddy_logic import parse_command, execute_command

load_dotenv()

app = Flask(__name__)

# WhatsApp API Config (WATI example)
WATI_API_URL = "https://app.wati.io/api/sendMessage"
WATI_API_TOKEN = os.getenv("WATI_API_TOKEN")

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify webhook token
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {WEBHOOK_VERIFY_TOKEN}":
        logging.warning("Unauthorized webhook access attempt")
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:
        data = request.json
        if not data:
            logging.warning("Received empty request data")
            return jsonify({"status": "error", "message": "Empty request data"}), 400

        sender_number = data.get('sender')
        message_text = data.get('message')

        if not sender_number or not message_text:
            logging.warning(f"Missing sender or message in request: {data}")
            return jsonify({"status": "error", "message": "Missing sender or message"}), 400

        # Process command
        parsed = parse_command(message_text)
        response_text = execute_command(parsed)

        # Send reply via WhatsApp
        payload = {
            "phone": sender_number,
            "message": response_text
        }
        headers = {"Authorization": f"Bearer {WATI_API_TOKEN}"}
        
        response = requests.post(WATI_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        logging.info(f"Sent message to {sender_number}: {response_text}")
        return jsonify({"status": "success"}), 200

    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to WATI: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500


if __name__ == "__main__":
    app.run(port=5000)
