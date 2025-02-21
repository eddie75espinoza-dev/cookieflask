import os
import sys
import json
import secrets
import shutil

use_db = '{{cookiecutter.use_db}}'


if use_db == "no":
    base_path = os.getcwd()
    app_path = os.path.join(
        base_path,
        'backend',
    )
    db_path = os.path.join(app_path, 'db')
    models_path = os.path.join(app_path, 'models')

    try:
        shutil.rmtree(db_path)
    except Exception:
        print("ERROR: cannot delete db path %s" % db_path)
        sys.exit(1)
    
    try:
        shutil.rmtree(models_path)
    except Exception:
        print("ERROR: cannot delete models path %s" % models_path)
        sys.exit(1)


def generate_secret_key():
    return secrets.token_urlsafe(32)

secret_key = generate_secret_key()
token_secret_key = generate_secret_key()

# Ruta al archivo cookiecutter.json
cookiecutter_json_path = os.path.join(os.getcwd(), 'cookiecutter.json')

# Actualizar el archivo cookiecutter.json con las claves generadas
if os.path.exists(cookiecutter_json_path):
    with open(cookiecutter_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Asegurarnos de que las claves secretas se agreguen al diccionario
    data['secret_key'] = secret_key
    data['token_secret_key'] = token_secret_key

    with open(cookiecutter_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    # Mostrar las claves generadas
    print(f"Secret Key: {secret_key}")
    print(f"Token Secret Key: {token_secret_key}")
else:
    print(f"ERROR: No se encontró el archivo {cookiecutter_json_path}")
    sys.exit(1)