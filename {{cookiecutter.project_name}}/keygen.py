"""
Para crear un token JWT (JSON Web Token) a manera de API KEY
"""

import datetime
import secrets
import uuid

import jwt


def set_jwt_token() -> tuple:
    secret_key = secrets.token_urlsafe(nbytes=32)

    jti = str(uuid.uuid4())

    payload = {
        "fresh": False,  # Previene revalidación
        "iat": datetime.datetime.now(),  # Emisión del token
        "jti": jti,  # Identificador único para el token
        "type": "access",  # Tipo de token
        "sub": "nombre-api",  # Identificador del usuario
        "nbf": datetime.datetime.now(),  # No aceptar antes
        "iss": "nombre-api",  # Identifica quién emitió el token
    }

    # Crea el token con clave
    secure_token = jwt.encode(payload, secret_key, algorithm="HS256")

    # Crea el token sin clave
    token = jwt.encode(payload, key="", algorithm="HS256")

    return secret_key, secure_token, token


if __name__ == "__main__":
    secret_key, secure_token, token = set_jwt_token()
    print(f"Clave segura -> {secret_key}\n")
    print(f"API KEY con clave segura -> {secure_token}\n")
    print(f"API KEY sin clave ->{token}")
