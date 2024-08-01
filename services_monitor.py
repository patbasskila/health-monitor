import os
import smtplib
import time
import win32serviceutil
import win32service
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration
services_to_monitor = ['Service1', 'Service2']  # Replace with your service names
check_interval = 60  # Time interval to check services (in seconds)
email_settings = {
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'smtp_user': 'you@example.com',
    'smtp_password': 'yourpassword',
    'from_email': 'you@example.com',
    'to_email': 'recipient@example.com'
}

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = email_settings['from_email']
    msg['To'] = email_settings['to_email']
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port'])
    server.starttls()
    server.login(email_settings['smtp_user'], email_settings['smtp_password'])
    text = msg.as_string()
    server.sendmail(email_settings['from_email'], email_settings['to_email'], text)
    server.quit()

def check_and_restart_service(service_name):
    try:
        status = win32serviceutil.QueryServiceStatus(service_name)[1]
        if status != win32service.SERVICE_RUNNING:
            win32serviceutil.StartService(service_name)
            time.sleep(5)
            status = win32serviceutil.QueryServiceStatus(service_name)[1]
            if status == win32service.SERVICE_RUNNING:
                message = f"Service {service_name} was stopped and has been restarted successfully."
                print(message)
                send_email(f'Service Restarted: {service_name}', message)
            else:
                message = f"Service {service_name} was stopped and failed to restart."
                print(message)
                send_email(f'Failed to Restart Service: {service_name}', message)
        else:
            print(f"Service {service_name} is running normally.")
    except Exception as e:
        message = f"Error checking service {service_name}: {str(e)}"
        print(message)
        send_email(f'Error with Service: {service_name}', message)

if __name__ == "__main__":
    while True:
        for service in services_to_monitor:
            check_and_restart_service(service)
        time.sleep(check_interval)
