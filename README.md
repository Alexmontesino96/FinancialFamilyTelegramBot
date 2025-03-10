# Financial Bot for Telegram

Bot de Telegram para gestionar finanzas familiares, registrar gastos, pagos y ver balances entre miembros.

## Configuración del Entorno

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd FinancialBotTelegram
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno:
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tu editor preferido
   ```

4. Variables de entorno en `.env`:
   - `BOT_TOKEN`: Token de tu bot de Telegram (obtenido de BotFather)
   - `API_BASE_URL`: URL de la API backend
   - `DEBUG`: Modo de depuración (True/False)
   - `ADMIN_CHAT_ID`: (Opcional) ID de chat para recibir notificaciones de errores

## Ejecución

Para iniciar el bot:
```bash
python main.py
```

## Estructura del Proyecto

- `main.py`: Punto de entrada principal del bot
- `config.py`: Configuración y estados de conversación
- `handlers/`: Manejadores para diferentes comandos y flujos de conversación
- `services/`: Servicios para interactuar con la API
- `utils/`: Utilidades y funciones auxiliares
- `ui/`: Componentes de interfaz de usuario (mensajes, teclados, etc.)
- `.env`: Archivo de configuración con variables de entorno (no incluido en el repositorio)
- `.env.example`: Ejemplo de archivo de configuración

## Flujos Principales

1. **Creación de Familia**: Permite crear una nueva familia y añadir miembros
2. **Registro de Gastos**: Permite registrar gastos compartidos
3. **Registro de Pagos**: Permite registrar pagos entre miembros
4. **Ver Balances**: Muestra quién debe dinero a quién
5. **Editar/Eliminar**: Permite modificar o eliminar gastos y pagos

## Despliegue

Este proyecto está preparado para ser desplegado en [Render](https://render.com/). Para instrucciones detalladas sobre cómo desplegar el bot, consulta el archivo [README-DEPLOY.md](README-DEPLOY.md).

### Archivos para despliegue

- `render.yaml`: Configuración para Render
- `Procfile`: Define cómo se inicia la aplicación
- `runtime.txt`: Especifica la versión de Python
- `health_check.py`: Implementa un endpoint de verificación de salud

### Consideraciones para producción

Para desplegar en producción, asegúrate de:

1. Configurar `DEBUG=False` en las variables de entorno
2. Usar HTTPS para la URL de la API backend
3. Configurar un ID de chat de administrador para recibir notificaciones de errores 