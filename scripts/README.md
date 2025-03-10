# Scripts de Utilidad para el Bot Financiero

Esta carpeta contiene scripts de utilidad para el bot financiero de Telegram.

## Verificación de Instancias Duplicadas

### Verificador Genérico

El script `check_bot_instances.py` verifica si hay múltiples instancias del bot ejecutándose y detiene las instancias adicionales para evitar conflictos. Este script se utiliza en entornos locales o de desarrollo.

Este script se ejecuta automáticamente al iniciar el bot, pero también puede ejecutarse manualmente:

```bash
python -m scripts.check_bot_instances
```

### Verificador Específico para Render

El script `render_instance_check.py` está diseñado específicamente para el entorno de Render. Utiliza un archivo de bloqueo para evitar que se inicien múltiples instancias del bot. Este script se utiliza automáticamente cuando el bot se ejecuta en Render.

Este script se puede ejecutar manualmente para probar su funcionamiento:

```bash
python -m scripts.render_instance_check
```

## Configuración del Chat de Administrador

El script `set_admin_chat.py` permite configurar el ID del chat de administrador para recibir notificaciones de errores del bot.

Para configurar el ID del chat de administrador:

```bash
python -m scripts.set_admin_chat <ID_DEL_CHAT>
```

Donde `<ID_DEL_CHAT>` es el ID del chat de Telegram donde quieres recibir las notificaciones de errores.

### ¿Cómo obtener el ID de un chat?

1. Agrega el bot [@userinfobot](https://t.me/userinfobot) a tu chat.
2. Envía cualquier mensaje al bot y te responderá con tu ID de usuario o el ID del chat.
3. Usa ese ID como parámetro para el script `set_admin_chat.py`.

## Instalación de Dependencias

Estos scripts requieren la instalación de algunas dependencias adicionales. Asegúrate de tener instalado `psutil` ejecutando:

```bash
pip install -r requirements.txt
``` 