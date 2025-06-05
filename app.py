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
app.secret_key = os.urandom(24)

# ──────────────────────────────────────────────────────────────
# Helper: Send email with debug output
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
# Routes
# ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", now=datetime.now())

@app.route("/properties")
def properties():
    try:
        with open("content/properties.json", "r") as f:
            properties_data = json.load(f)
    except Exception as e:
        print(f"[Property Load Error] {e}")
        properties_data = []
    return render_template("properties.html", properties=properties_data, now=datetime.now())

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

@app.route("/calendar")
def calendar():
    try:
        with open("content/calendar_data.json", "r") as f:
            calendar_data = json.load(f)
    except Exception as e:
        print(f"[Calendar Load Error] {e}")
        calendar_data = {}

    return render_template("calendar.html", bookings=calendar_data, now=datetime.now())

@app.route("/calendar/<slug>")
def calendar_by_property(slug):
    try:
        with open("content/properties.json", "r") as f:
            properties = json.load(f)
        property_match = next((p for p in properties if p["slug"] == slug), None)
    except Exception as e:
        print(f"[Property Lookup Error] {e}")
        property_match = None

    try:
        with open("content/calendar_data.json", "r") as f:
            all_data = json.load(f)
            bookings = all_data.get(slug, [])
    except Exception as e:
        print(f"[Calendar Load Error] {e}")
        bookings = []

    if not property_match:
        flash("Property not found for calendar view.", "danger")
        return redirect("/calendar")

    return render_template("calendar_property.html", property=property_match, bookings=bookings, now=datetime.now())

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Name, email, and message are required.", "danger")
            return redirect("/contact")

        full_message = (
            f"New contact form submission:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Message:\n{message}"
        )

        if send_email(f"New Inquiry from {name}", full_message, EMAIL_ADDRESS):
            flash("Your message has been sent successfully!", "success")
        else:
            flash("There was an error sending your message. Please try again.", "danger")

        return redirect("/contact")

    return render_template("contact.html", now=datetime.now())

@app.route("/inquire", methods=["POST"])
def inquire():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    property_name = request.form.get("property", "Unknown Property")

    if not name or not email or not message:
        flash("Name, email, and message are required.", "danger")
        return redirect(request.referrer or "/properties")

    full_message = (
        f"New inquiry for: {property_name}\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Message:\n{message}"
    )

    if send_email(f"Inquiry for {property_name} from {name}", full_message, EMAIL_ADDRESS):
        flash("Your inquiry has been sent!", "success")
    else:
        flash("There was an error sending your inquiry. Please try again.", "danger")

    return redirect(request.referrer or "/properties")

# ──────────────────────────────────────────────────────────────
# Run the app
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
