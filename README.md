# Consulta de Cargos en el Portal de Actos Públicos Digitales (APD) de la Provincia de Buenos Aires

Este proyecto permite consultar los cargos publicados disponibles en el Portal de Actos Públicos Digitales (APD) de la Provincia de Buenos Aires para los distritos y cargos de interés especificados. Los resultados se envían a un correo electrónico configurado en las variables de acción del repositorio.

## Requisitos

- Git
- Una cuenta de GitHub
- Una cuenta de correo electrónico (preferiblemente Gmail)
- Autenticación en dos pasos (2FA) habilitada en la cuenta de correo electrónico

## Instrucciones

### 1. Clonar el repositorio

Primero, crea un fork de este repo desde github para tener tu propio repo.

### 2. Configurar las variables de acción

En tu repositorio de GitHub, ve a la sección de **Settings** y luego a **secrets and variables** y luego a **Actions**. Configura las siguientes variables de acción:

- `LISTA_DISTRITOS`: Lista de distritos de interés, separados por comas. ej: berazategui,quilmes,avellaneda
- `LISTA_CARGOS`: Lista de cargos de interés, separados por comas.  ej: ODM,TCI,/PR
- `EMAIL_SEND`: Correo electrónico al que se enviarán los reportes. ej: juan_perez@gmail.com.ar
- `SMTP_PORT`: Puerto que usa el servicio SMTP (lo que permite enviar mails desde python). ej: gmail es 587
- `SMTP_SERVER`: Servicio que envía los mails. ej: gmail es smtp.gmail.com


### 3. Configurar los secretos de GitHub

Para enviar correos electrónicos, necesitas configurar los secretos de GitHub con las credenciales de tu cuenta de correo. Ve a **Settings** > **Secrets and variables** > **Actions** y agrega los siguientes secretos:

- `EMAIL_ADDRESS`: Correo electrónico desde el cual se enviarán los reportes.
- `EMAIL_PASSWORD`: Contraseña de la aplicación del correo electrónico. (hay que crearlas desde gmail, se explica a continuación)

### 4. Crear una contraseña de aplicación en Gmail

Si utilizás Gmail, Seguí estos pasos, si no usas Gmail...arreglátelas 😆:

1. Habilita la autenticación en dos pasos (2FA) en tu cuenta de Google si no lo has hecho ya.
2. Ve [a esta pag de google](http://security.google.com/settings/security/apppasswords) y crea una contraseña.
4. Copia la contraseña generada y úsala como `EMAIL_PASSWORD` en los secretos de GitHub. 
IMPORTANTE, una vez que guardes el secret, no se puede volver a visualizar, ni siquiera por vos mismo, por lo que si necesitas esa contraseña para algo más, anótala en algún lugar seguro.

### 5. Ejecutar el flujo de trabajo

Una vez configuradas las variables y secretos, el flujo de trabajo se ejecutará automáticamente según la configuración del repositorio, actualmente está configurado para ejectuarse cada vez que se genera un cambió en el repositorio (push o pull request) y todos los días a las 18:30 hora argentina, pero podés cambiar esto a gusto modificando la variable "cron" en el siguiente archivo:

[REPO]/.github/workflows/blank.yml

Si necesitas entender cómo funciona el cron, podés utilizar [esta página.](https://crontab.guru/)
Los reportes se enviarán al correo electrónico especificado.

---

¡Eso es todo! Si tienes alguna pregunta o necesitas ayuda adicional, no dudes en preguntar. 😊
Ing. Bracco Leonel.
