from flask import Flask, request, jsonify
from self_esteem_system import SelfEsteemSystem
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
self_esteem_system = SelfEsteemSystem()

@app.route('/')
def index():
    return "Self-Esteem System Webhook Listener is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.is_json:
        data = request.get_json()
        app.logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")

        # Extract relevant data from Formspree submission
        user_email = data.get('email')
        
        # Formspree usually sends form fields directly.
        # We need to map them to the expected inputs for self_esteem_system.
        # Assuming 'answers' comes as a JSON string
        answers_str = data.get('answers')
        
        if not user_email or not answers_str:
            app.logger.error("Missing 'email' or 'answers' in webhook data.")
            return jsonify({"status": "error", "message": "Missing email or answers"}), 400

        try:
            responses = json.loads(answers_str)
            if not isinstance(responses, list):
                raise ValueError("Answers must be a list.")
        except json.JSONDecodeError:
            app.logger.error(f"Failed to decode 'answers' JSON string: {answers_str}")
            return jsonify({"status": "error", "message": "Invalid JSON for answers"}), 400
        except ValueError as e:
            app.logger.error(f"Invalid answers format: {e}")
            return jsonify({"status": "error", "message": str(e)}), 400

        # Formspree doesn't provide user_name directly,
        # we can try to extract from email or use a placeholder
        user_name = user_email.split('@')[0] if user_email else "고객" 
        
        # The frontend script.js sends these in hidden fields:
        # total_score, core_score, compassion_score, stability_score, growth_score, social_score
        # We will re-calculate these in the backend for integrity,
        # but the original script also needs a 'responses' list.
        # For now, we will use the 'responses' directly.
        
        try:
            # Process results using the SelfEsteemSystem
            results = self_esteem_system.process_test_results(
                user_name=user_name,
                user_email=user_email,
                responses=responses
            )

            # Here you would integrate an actual email sending service (e.g., SendGrid, Mailgun, SMTP)
            # For demonstration, we'll just log the email bodies.
            app.logger.info(f"Generated basic email for {user_email}:")
            app.logger.info(results['emails']['basic']['body'])
            
            # The system also generates intermediate and detailed emails with delays
            # In a real system, you would queue these emails to be sent at the specified delays
            # (e.g., using a task queue like Celery or a scheduled job).
            # For this MVP, we'll just acknowledge their generation.

            return jsonify({"status": "success", "message": "Results processed and emails generated (not sent yet).", "data": results}), 200

        except Exception as e:
            app.logger.error(f"Error processing test results: {e}", exc_info=True)
            return jsonify({"status": "error", "message": "Internal server error"}), 500
    else:
        app.logger.warning("Webhook received non-JSON content.")
        return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 400

if __name__ == '__main__':
    # For local development, use python -m flask run
    # For production, use a WSGI server like Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
