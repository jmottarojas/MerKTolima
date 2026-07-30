#!/usr/bin/env python3
"""
Configuración de ejemplo para envío real de emails
Este archivo muestra cómo configurar diferentes servicios de email
"""

# =============================================================================
# CONFIGURACIÓN PARA DJANGO EMAIL BACKEND
# =============================================================================

# Agregar a settings.py de Django:
DJANGO_EMAIL_SETTINGS = {
    # Gmail SMTP
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_HOST_USER': 'tu-email@gmail.com',
    'EMAIL_HOST_PASSWORD': 'tu-app-password',  # Usar App Password, no contraseña normal
    'DEFAULT_FROM_EMAIL': 'Merktolima <tu-email@gmail.com>',
    
    # Outlook/Hotmail SMTP
    # 'EMAIL_HOST': 'smtp-mail.outlook.com',
    # 'EMAIL_PORT': 587,
    # 'EMAIL_USE_TLS': True,
    
    # Para desarrollo (emails en consola)
    # 'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
}

# =============================================================================
# FUNCIÓN REAL PARA ENVÍO DE EMAILS
# =============================================================================

def send_verification_email_real(email, verification_code, first_name):
    """
    Función real para enviar emails de verificación
    Reemplaza la función simulada en views.py
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.conf import settings
    
    try:
        # Renderizar template HTML del email
        html_message = render_to_string('emails/verification_email.html', {
            'first_name': first_name,
            'verification_code': verification_code,
            'site_name': 'Merktolima',
        })
        
        # Versión texto plano
        plain_message = strip_tags(html_message)
        
        # Enviar email
        send_mail(
            subject='Verifica tu email en Merktolima',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# =============================================================================
# TEMPLATE HTML PARA EMAIL DE VERIFICACIÓN
# =============================================================================

# Crear archivo: frontend/templates/emails/verification_email.html
VERIFICATION_EMAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verifica tu email - {{ site_name }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #dc3545;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
        .content {
            background-color: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 8px 8px;
        }
        .code {
            background-color: white;
            border: 2px solid #dc3545;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .code-number {
            font-size: 32px;
            font-weight: bold;
            color: #dc3545;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }
        .button {
            display: inline-block;
            background-color: #dc3545;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>¡Bienvenido a {{ site_name }}!</h1>
    </div>
    
    <div class="content">
        <h2>Hola {{ first_name }},</h2>
        
        <p>Gracias por registrarte en {{ site_name }}. Para completar tu registro, necesitamos verificar tu dirección de email.</p>
        
        <div class="code">
            <p><strong>Tu código de verificación es:</strong></p>
            <div class="code-number">{{ verification_code }}</div>
            <p><small>Este código expira en 10 minutos</small></p>
        </div>
        
        <p>Ingresa este código en la página de verificación para activar tu cuenta.</p>
        
        <p>Si no solicitaste este registro, puedes ignorar este email de forma segura.</p>
        
        <div class="footer">
            <p>© 2024 {{ site_name }}. Todos los derechos reservados.</p>
            <p>Este es un email automático, por favor no respondas a este mensaje.</p>
        </div>
    </div>
</body>
</html>
"""

# =============================================================================
# CONFIGURACIÓN CON SERVICIOS EXTERNOS
# =============================================================================

# SendGrid
SENDGRID_CONFIG = {
    'api_key': 'tu-sendgrid-api-key',
    'from_email': 'noreply@merktolima.com',
    'template_id': 'tu-template-id',
}

# Mailgun
MAILGUN_CONFIG = {
    'api_key': 'tu-mailgun-api-key',
    'domain': 'tu-dominio.mailgun.org',
    'from_email': 'noreply@merktolima.com',
}

# AWS SES
AWS_SES_CONFIG = {
    'aws_access_key_id': 'tu-access-key',
    'aws_secret_access_key': 'tu-secret-key',
    'region_name': 'us-east-1',
    'from_email': 'noreply@merktolima.com',
}

# =============================================================================
# INSTRUCCIONES DE IMPLEMENTACIÓN
# =============================================================================

IMPLEMENTATION_STEPS = """
PASOS PARA IMPLEMENTAR ENVÍO REAL DE EMAILS:

1. CONFIGURAR DJANGO SETTINGS:
   - Agregar configuración EMAIL_* a settings.py
   - Configurar DEFAULT_FROM_EMAIL

2. CREAR TEMPLATE DE EMAIL:
   - Crear carpeta: frontend/templates/emails/
   - Crear archivo: verification_email.html
   - Usar el HTML de arriba como base

3. REEMPLAZAR FUNCIÓN EN VIEWS.PY:
   - Reemplazar send_verification_email() con send_verification_email_real()
   - Importar las funciones necesarias de Django

4. CONFIGURAR PROVEEDOR DE EMAIL:
   - Gmail: Habilitar 2FA y crear App Password
   - SendGrid: Crear cuenta y obtener API key
   - Mailgun: Configurar dominio y obtener credenciales
   - AWS SES: Configurar IAM y verificar dominio

5. PROBAR EN DESARROLLO:
   - Usar EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   - Los emails aparecerán en la consola

6. VARIABLES DE ENTORNO:
   - Nunca hardcodear credenciales
   - Usar variables de entorno para producción
   - Ejemplo: EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

7. MONITOREO:
   - Implementar logs para emails enviados
   - Manejar errores de envío
   - Configurar alertas para fallos
"""

if __name__ == "__main__":
    print("📧 CONFIGURACIÓN DE EMAIL PARA MERKTOLIMA")
    print("="*50)
    print(IMPLEMENTATION_STEPS)