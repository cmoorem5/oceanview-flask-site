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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/properties")
def properties():
    return render_template("properties.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form.get("phone", "")
        message = request.form["message"]

        full_message = (
            f"New contact form submission:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Message:\n{message}"
        )

        try:
            msg = EmailMessage()
            msg.set_content(full_message)
            msg["Subject"] = f"New Inquiry from {name}"
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = EMAIL_ADDRESS  # Or use a separate destination if preferred

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)

            flash("Your message has been sent successfully!", "success")
            return redirect("/contact")

        except Exception as e:
            flash("There was an error sending your message. Please try again.", "danger")
            print(f"Error: {e}")
            return redirect("/contact")

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
