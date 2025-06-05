from flask import Flask, render_template, request, redirect, flash
import os
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────
# Load environment variables
# ──────────────────────────────────────────────────────────────
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

# ──────────────────────────────────────────────────────────────
# Initialize Flask app
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# ──────────────────────────────────────────────────────────────
# Helper: Send email
# ──────────────────────────────────────────────────────────────
def send_email(subject, body, to_email):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return True
    except Exception as e:
        print(f"[Email Error] {e}")
        return False

# ──────────────────────────────────────────────────────────────
# Route: Homepage
# ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", now=datetime.now())

# ──────────────────────────────────────────────────────────────
# Route: Properties Page (load JSON)
# ──────────────────────────────────────────────────────────────
@app.route("/property/<slug>")
def property_detail(slug):
    try:
        with open("content/properties.json", "r") as f:
            properties = json.load(f)
        property_match = next((p for p in properties if p["slug"] == slug), None)
    except Exception as e:
        print(f"[Property Detail Error] {e}")
        property_match = None

    if not property_match:
        flash("Property not found.", "danger")
        return redirect("/properties")

    return render_template("property_detail.html", property=property_match, now=datetime.now())
# ──────────────────────────────────────────────────────────────
# Route: Contact Form (GET + POST)
# ──────────────────────────────────────────────────────────────
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        # Validate required fields
        if not name or not email or not message:
            flash("Name, email, and message are required.", "danger")
            return redirect("/contact")

        # Compose email message
        full_message = (
            f"New contact form submission:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Message:\n{message}"
        )

        # Attempt to send email
        if send_email(f"New Inquiry from {name}", full_message, EMAIL_ADDRESS):
            flash("Your message has been sent successfully!", "success")
        else:
            flash("There was an error sending your message. Please try again.", "danger")

        return redirect("/contact")

    return render_template("contact.html", now=datetime.now())

# ──────────────────────────────────────────────────────────────
# Run the app
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
