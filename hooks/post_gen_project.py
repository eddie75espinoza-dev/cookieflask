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

env_dev_file = os.path.join(os.getcwd(), '.env.dev')

if os.path.exists(env_dev_file):
    with open(env_dev_file, 'r') as dev_file:
        content = dev_file.read()
    content = content.replace('_secret_key_to_replace_', secret_key)
    with open(env_dev_file, 'w') as dev_file:
        dev_file.write(content)
    print(f"✅ Claves secretas actualizadas en {env_dev_file}")
else:
    print(f"⚠️ Archivo {env_dev_file} no encontrado.")


env_prod_file = os.path.join(os.getcwd(), '.env.prod')

if os.path.exists(env_prod_file):
    with open(env_prod_file, 'r') as prod_file:
        content = prod_file.read()
    content = content.replace('_secret_key_to_replace_', secret_key)
    with open(env_prod_file, 'w') as prod_file:
        prod_file.write(content)
    print(f"✅ Claves secretas actualizadas en {env_prod_file}")
else:
    print(f"⚠️ Archivo {env_prod_file} no encontrado.")