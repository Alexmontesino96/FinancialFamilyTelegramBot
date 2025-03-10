# Despliegue en Render

Este documento proporciona instrucciones para desplegar el Financial Bot for Telegram en [Render](https://render.com/).

## Requisitos previos

1. Una cuenta en [Render](https://render.com/)
2. Un bot de Telegram creado con [BotFather](https://t.me/botfather)
3. El código fuente de la aplicación en un repositorio Git (GitHub, GitLab, etc.)

## Pasos para el despliegue

### 1. Preparar el repositorio

Asegúrate de que tu repositorio incluya los siguientes archivos:

- `render.yaml` - Configuración para Render
- `Procfile` - Define cómo se inicia la aplicación
- `runtime.txt` - Especifica la versión de Python
- `requirements.txt` - Lista de dependencias
- `health_check.py` - Implementa un endpoint de verificación de salud

### 2. Crear un nuevo servicio en Render

1. Inicia sesión en tu cuenta de Render
2. Haz clic en "New" y selecciona "Blueprint" (si quieres usar el archivo render.yaml) o "Web Service" (para configuración manual)

#### Opción A: Usando Blueprint (recomendado)

1. Conecta tu repositorio Git
2. Render detectará automáticamente el archivo `render.yaml` y configurará el servicio
3. Haz clic en "Apply" para crear el servicio

#### Opción B: Configuración manual

1. Conecta tu repositorio Git
2. Configura el servicio:
   - **Name**: `financial-bot-telegram` (o el nombre que prefieras)
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free (o el plan que prefieras)

### 3. Configurar variables de entorno

En la sección "Environment" de tu servicio en Render, configura las siguientes variables:

- `BOT_TOKEN`: El token de tu bot de Telegram (obtenido de BotFather)
- `API_BASE_URL`: La URL de tu API backend
- `DEBUG`: `False` (para producción)
- `ADMIN_CHAT_ID`: (Opcional) Tu ID de chat de Telegram para recibir notificaciones de errores

### 4. Desplegar el servicio

1. Haz clic en "Create Web Service" o "Apply Blueprint"
2. Render comenzará a construir y desplegar tu aplicación
3. Una vez completado, tu bot estará en funcionamiento

## Verificación del despliegue

Para verificar que tu bot está funcionando correctamente:

1. Abre Telegram y busca tu bot
2. Envía el comando `/start`
3. El bot debería responder con el mensaje de bienvenida

## Monitoreo y logs

Render proporciona herramientas para monitorear tu aplicación:

1. En el panel de tu servicio, ve a la pestaña "Logs"
2. Aquí puedes ver los logs de tu aplicación en tiempo real
3. También puedes configurar alertas para ser notificado cuando ocurran errores

## Solución de problemas

Si tu bot no responde o encuentras errores:

1. Verifica los logs en Render para identificar el problema
2. Asegúrate de que todas las variables de entorno estén configuradas correctamente
3. Verifica que el token del bot sea válido
4. Comprueba que la API backend esté accesible desde Render

## Consideraciones adicionales

- **Modo Always On**: Por defecto, los servicios gratuitos de Render se "duermen" después de 15 minutos de inactividad. Considera actualizar a un plan pago si necesitas que tu bot esté siempre disponible.
- **Límites de recursos**: Los planes gratuitos tienen límites de CPU y memoria. Monitorea el uso de recursos de tu aplicación.
- **Dominio personalizado**: Si quieres usar un dominio personalizado para tu API, puedes configurarlo en la sección "Settings" de tu servicio. 