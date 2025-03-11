import os
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from tabulate import tabulate
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


orden_distritos = {'QUILMES':2,'AVELLANEDA':1,'BERAZATEGUI':0}

ofertas_por_distrito = df.groupby(['descdistrito','descripcioncargo'])['ige'].nunique().reset_index()
ofertas_por_distrito.columns = ['Distrito','Cargo','Cantidad']
ofertas_por_distrito["order"] = ofertas_por_distrito.Distrito.map(orden_distritos)
ofertas_por_distrito = ofertas_por_distrito.sort_values(by=['order','Cantidad'],ascending=False)
ofertas_por_distrito.drop(columns="order",inplace=True)
ofertas_por_distrito = tabulate(
    ofertas_por_distrito, 
    headers=ofertas_por_distrito.columns, 
    tablefmt="html",
    showindex=False,
)



ofertas_por_escuela = df.groupby(['descdistrito','escuela','domiciliodesempeno','descripcioncargo'])['ige'].nunique().reset_index()
ofertas_por_escuela.columns = ['Distrito','Escuela','Dirección','Cargo','Cantidad']
ofertas_por_escuela["order"] = ofertas_por_escuela.Distrito.map(orden_distritos)
ofertas_por_escuela = ofertas_por_escuela.sort_values(by=['order','Cantidad'],ascending=False)
ofertas_por_escuela.drop(columns="order",inplace=True)
ofertas_por_escuela = tabulate(
    ofertas_por_escuela, 
    headers=ofertas_por_escuela.columns, 
    tablefmt="html",
    showindex=False,
)

cantidad_ofertas = df["ige"].nunique()

subject = f'Hay {cantidad_ofertas} ofertas disponibles del día {datetime.now()}'
body = f'''\
<html>
  <body>
<p><strong>Espero que le sea &uacute;til</strong></p>
<ul>
<li>Tenemos por distrito:</li>
</ul>
<p>{ofertas_por_distrito}</p>
<ul>
<li>Y por escuela:</li>
</ul>
<p>{ofertas_por_escuela}</p>
<p>&nbsp;</p>
<p>Adjunto detalle completo</p>
  </body>
</html>
'''

# Email content
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))

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
