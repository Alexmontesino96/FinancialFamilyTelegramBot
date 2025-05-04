import qrcode
from io import BytesIO



def create_qr_code(codigo):
    """Crea un código QR con el texto proporcionado y lo guarda como 'mi_qr.png'."""
    # Crear un objeto QR
    qr = qrcode.QRCode(
        version=1,               # Controla el tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,             # El tamaño de cada "cuadradito" del QR
        border=4,                # El grosor del borde en cuadros
    )

    # Agregar el texto al objeto QR
    qr.add_data(codigo)
    qr.make(fit=True)

    # Crear la imagen
    img = qr.make_image(fill_color="black", back_color="white")

    bio = BytesIO()
    bio.name = 'codigo_qr.png'  # Nombre "ficticio" para el archivo
    img.save(bio, 'PNG')
    bio.seek(0)

    return bio

