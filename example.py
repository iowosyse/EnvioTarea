import base64
import mimetypes
import os
import sys

import msal
import requests


# =========================================================
# CONFIGURACIÓN
# =========================================================

CLIENT_ID = "CLIENT_ID"
TENANT_ID = "TENANT_ID"

DESTINATARIO = "DESTINATARIO"

NUMERO_CONTROL = "XXXXXXXX"
NOMBRE = "NOMBRE"

MATERIA = "Lenguajes y Autómatas 1"

# =========================================================

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Mail.Send"]

CACHE_FILE = "token_cache.bin"


def cargar_cache():
    cache = msal.SerializableTokenCache()

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())

    return cache


def guardar_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def obtener_token():
    cache = cargar_cache()

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    resultado = None

    cuentas = app.get_accounts()

    if cuentas:
        resultado = app.acquire_token_silent(
            SCOPES,
            account=cuentas[0]
        )

    if not resultado:
        flujo = app.initiate_device_flow(scopes=SCOPES)

        if "user_code" not in flujo:
            raise RuntimeError(
                "No se pudo iniciar la autenticación:\n"
                + str(flujo)
            )

        print()
        print(flujo["message"])
        print()

        resultado = app.acquire_token_by_device_flow(flujo)

    guardar_cache(cache)

    if "access_token" not in resultado:
        raise RuntimeError(
            resultado.get(
                "error_description",
                "No se pudo obtener el token."
            )
        )

    return resultado["access_token"]


def crear_adjunto(ruta):
    with open(ruta, "rb") as archivo:
        contenido = base64.b64encode(
            archivo.read()
        ).decode("utf-8")

    tipo_mime, _ = mimetypes.guess_type(ruta)

    if tipo_mime is None:
        tipo_mime = "application/octet-stream"

    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": os.path.basename(ruta),
        "contentType": tipo_mime,
        "contentBytes": contenido
    }


def enviar_correo(numero_tarea, ruta_archivo):
    token = obtener_token()

    asunto = f"Tarea {numero_tarea} de {MATERIA}"

    cuerpo = f"""{NUMERO_CONTROL}
{NOMBRE}"""

    mensaje = {
        "message": {
            "subject": asunto,

            "body": {
                "contentType": "Text",
                "content": cuerpo
            },

            "toRecipients": [
                {
                    "emailAddress": {
                        "address": DESTINATARIO
                    }
                }
            ],

            "attachments": [
                crear_adjunto(ruta_archivo)
            ]
        }
    }

    respuesta = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=mensaje
    )

    if respuesta.status_code == 202:
        print("\nCorreo enviado correctamente.")
    else:
        print("\nError al enviar el correo.")
        print("Código:", respuesta.status_code)
        print(respuesta.text)


def main():
    print("=== Envío de tareas ===\n")

    numero_tarea = input(
        "Número de tarea: "
    ).strip()

    ruta_archivo = input(
        "Ruta del archivo: "
    ).strip()

    # Permite arrastrar el archivo a la terminal;
    # Windows suele poner comillas alrededor.
    ruta_archivo = ruta_archivo.strip('"')

    if not os.path.isfile(ruta_archivo):
        print("\nEl archivo especificado no existe.")
        sys.exit(1)

    asunto = f"Tarea {numero_tarea} de {MATERIA}"

    print()
    print(f"Asunto:       {asunto}")
    print(f"Destinatario: {DESTINATARIO}")
    print(f"Archivo:      {os.path.basename(ruta_archivo)}")
    print()
    print("Contenido:")
    print("----------------")
    print(NUMERO_CONTROL)
    print(NOMBRE)
    print("----------------")

    confirmar = input("\n¿Enviar? [s/N]: ").strip().lower()

    if confirmar != "s":
        print("Envío cancelado.")
        return

    enviar_correo(numero_tarea, ruta_archivo)


if __name__ == "__main__":
    main()
