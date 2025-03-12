import os
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from tabulate import tabulate
import io
import subprocess



lista_codigos_cargos = ['CCD',
                        'CCS',
                        'CYC',
                        'CYT',
                        'EAD',
                        'ECS',
                        'IAC',
                        'OCL',
                        'OCS',
                        'ODM',
                        'TCI',
                        '/PR',
                        '+3E',
                        'CCC',
                        'PEE',
                        'PRA',
                        'PRT',
                        'YCS',
                        '/3D',
                        '/3E',
                        'CMN',
                        'EDP',
                        'MKS',
                        'TLC']

lista_distritos = ['berazategui','quilmes','avellaneda']
lista_distritos_formateados = "%20".join(lista_distritos)

result = subprocess.run(f'''curl 'https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select?q=*%3A*&rows=10000&facet=true&facet.field=descdistrito&facet.field=descnivelmodalidad&facet.field=cargo&facet.field=estado&facet.limit=20000&facet.mincount=1&json.nl=map&fq=descdistrito%3A{lista_distritos_formateados}&fq=estado:Publicada&wt=csv' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Connection: keep-alive' -H 'Cookie: _ga=GA1.3.1448501204.1598045085; _gid=GA1.3.1833139648.1598875839; IPCZQX034ee7c6fd=0100c3000a1432ac8ea31b21c67f7acb521691f8; ZNPCQ003-33383400=a89f2a51; ZNPCQ003-32383300=4e5b6dbe' -H 'Upgrade-Insecure-Requests: 1' | iconv -f iso-8859-1 -t UTF-8//TRANSLIT''', shell=True, capture_output=True, text=True)
df_sin_filtrar = pd.read_csv(io.StringIO(result.stdout))
df_sin_filtrar["areaincumbencia"] = df_sin_filtrar["areaincumbencia"].str.replace(" ","") #Por las dudas
df_sin_filtrar["areaincumbencia"] = df_sin_filtrar["areaincumbencia"].str.upper() #Por las dudas
df = df_sin_filtrar[df_sin_filtrar["areaincumbencia"].isin(lista_codigos_cargos)]

file_attachment = "lista_ofertas.xlsx"
df.to_excel(file_attachment,index=False)



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
with open(file_attachment, 'rb') as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={file_attachment}')
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
