from flask import Flask, render_template, request, redirect, flash
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 📬 Email sending helper
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

# 🌐 Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/properties")
def properties():
    return render_template("properties.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    errors = {}

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        # Basic validation
        if not name:
            errors["name"] = "Name is required."
        if not email:
            errors["email"] = "Email is required."
        if not message:
            errors["message"] = "Message is required."

        if errors:
            flash("Please correct the errors below and try again.", "danger")
            return render_template("contact.html", errors=errors, request=request)

        # Compose email message
        full_message = (
            f"New contact form submission:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Message:\n{message}"
        )

        if send_email(f"New Inquiry from {name}", full_message, EMAIL_ADDRESS):
            flash("Your message has been sent successfully!", "success")
            return redirect("/contact")
        else:
            flash("There was an error sending your message. Please try again.", "danger")

    return render_template("contact.html", errors=errors)
    
if __name__ == "__main__":
    app.run(debug=True)
