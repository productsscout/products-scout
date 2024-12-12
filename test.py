import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_business(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port):
    try:
        # Create the email components
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject

        # Add email body
        message.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:  # Using SSL for port 465
            server.login(sender_email, sender_password)  # Login to the SMTP server

            # Send the email
            server.send_message(message)
            print(f"Email sent successfully to {recipient_email}")

    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Please check your email and password.")
    except smtplib.SMTPConnectError:
        print("Failed to connect to the SMTP server. Check the server and port settings.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    sender_email = "no-reply@productsscout.com"  # Replace with your business email
    sender_password = "UUDoon233620000@1098"  # Replace with your business email password
    recipient_email = "avi95461@gmail.com"  # Replace with recipient email
    subject = "Test Email from Business Account"
    body = "This is a test email sent using Python and smtplib with a business email."

    # SMTP configuration for your business email
    smtp_server = "smtpout.secureserver.net"  # Replace with your domain's SMTP server (check with your provider)
    smtp_port = 465  # Common port for SSL

    send_email_business(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port)
