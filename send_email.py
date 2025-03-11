import os
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
# Load the CSV


files = os.listdir("./DATA/")
files.sort(reverse=True)
file = files[0] #me quedo con el último
csv_file = f'./DATA/{file}'  # Replace with the path to your CSV file
df = pd.read_csv(csv_file)

# Retrieve sensitive information from GitHub secrets
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')  # Default to Gmail
smtp_port = os.getenv('SMTP_PORT', '587')  # Default to 587
sender_email = os.getenv('EMAIL_ADDRESS')  # Your email address
password = os.getenv('EMAIL_PASSWORD')  # Your email password (or app password)
receiver_email = os.getenv('EMAIL_SEND') 


ofertas_por_distrito = df.groupby(['descdistrito','descripcioncargo'])['ige'].nunique().reset_index()
ofertas_por_distrito.columns = ['Distrito','Cargo','Cantidad']



ofertas_por_escuela = df.groupby(['escuela','domiciliodesempeno','descripcioncargo'])['ige'].nunique().reset_index()
ofertas_por_escuela.columns = ['Escuela','Dirección','Cargo','Cantidad']

cantidad_ofertas = df["ige"].nunique()

subject = f'Hay {cantidad_ofertas} ofertas disponibles del día {datetime.now}'
body = f'''Espero que le sea útil
Tenemos por distrito:
{ofertas_por_distrito}

Y por escuela:
{ofertas_por_escuela}

Adjunto detalle completo
'''

# Email content
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

# Attach CSV file
with open(csv_file, 'rb') as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={csv_file}')
    msg.attach(part)

# Send email
try:
    with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print("Email sent successfully")
except Exception as e:
    print(f"Failed to send email: {e}")
