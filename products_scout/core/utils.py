import requests
import logging
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize logger
logger = logging.getLogger(__name__)

# =================================================
# CAPTCHA Verification
# =================================================
def verify_captcha(token):
    """
    Verify CAPTCHA using Google's reCAPTCHA API.
    :param token: CAPTCHA token from the frontend.
    :return: Boolean indicating if CAPTCHA is valid.
    """
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': token,
    }

    try:
        # Make the request to Google's reCAPTCHA API
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status()
        result = response.json()

        # Log the result for debugging
        if result.get("success", False):
            logger.info("CAPTCHA verification successful.")
        else:
            logger.warning(f"CAPTCHA verification failed: {result}")

        return result.get("success", False)

    except requests.RequestException as e:
        # Log the error for debugging
        logger.error(f"CAPTCHA verification request failed: {e}")
        return False

# =================================================
# Email Sending via SMTP
# =================================================
def send_email_smtp(subject, body, recipient_email, is_html=False, sender_email=None):
    """
    Send an email using SMTP.
    :param subject: Email subject.
    :param body: Email body (plain text or HTML).
    :param recipient_email: Recipient email address.
    :param is_html: Boolean indicating if the email is HTML (default: False).
    :param sender_email: Sender email address (default: settings.DEFAULT_FROM_EMAIL).
    :return: Boolean indicating if the email was sent successfully.
    """
    smtp_server = settings.SMTP_SERVER
    port = settings.SMTP_PORT
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD

    # Use the default sender email if not provided
    sender_email = sender_email or settings.DEFAULT_FROM_EMAIL

    try:
        # Establish a secure SMTP connection
        server = smtplib.SMTP_SSL(smtp_server, port)
        server.login(username, password)

        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Attach plain text or HTML content
        if is_html:
            message.attach(MIMEText(body, "html"))
        else:
            message.attach(MIMEText(body, "plain"))

        # Send the email
        server.sendmail(sender_email, recipient_email, message.as_string())
        logger.info(f"Email sent successfully to {recipient_email}")
        server.quit()
        return True

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred while sending email to {recipient_email}: {e}")
        return False

    except Exception as e:
        logger.error(f"An error occurred while sending email to {recipient_email}: {e}")
        return False
