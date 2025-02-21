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

# Genera nuevas claves
secret_key = generate_secret_key()
token_secret_key = generate_secret_key()

# Actualiza el archivo .env con los nuevos valores
env_file = os.path.join(os.getcwd(), '.env.dev')
if os.path.exists(env_file):
    with open(env_file, 'r') as file:
        content = file.read()
    content = content.replace('_secret_key_to_replace_', secret_key)
    with open(env_file, 'w') as file:
        file.write(content)
    print(f"✅ Claves secretas actualizadas en {env_file}")
else:
    print("⚠️ Archivo .env no encontrado.")