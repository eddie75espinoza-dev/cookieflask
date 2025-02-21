import os
import sys
import secrets
import shutil


def generate_secret_key():
    return secrets.token_urlsafe(32)

use_db = '{{cookiecutter.use_db}}'
secret_key = '{{cookiecutter.secret_key}}'
new_secret_key = generate_secret_key()
env_dev_file = os.path.join(os.getcwd(), '.env.dev')
env_prod_file = os.path.join(os.getcwd(), '.env.prod')


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

if secret_key != "If you don't change it, it will be changed.":
    if os.path.exists(env_dev_file):
        with open(env_dev_file, 'r') as dev_file:
            content = dev_file.read()
        content = content.replace("If you don't change it, it will be changed.", new_secret_key)
        
        with open(env_dev_file, 'w') as dev_file:
            dev_file.write(content)
        print(f"✅ Secret keys updated in {env_dev_file}")

    else:
        print(f"⚠️ File {env_dev_file} not found.")


    if os.path.exists(env_prod_file):
        with open(env_prod_file, 'r') as prod_file:
            content = prod_file.read()
        content = content.replace("If you don't change it, it will be changed.", new_secret_key)
        
        with open(env_prod_file, 'w') as prod_file:
            prod_file.write(content)
        print(f"✅ Secret keys updated in {env_prod_file}")

    else:
        print(f"⚠️ File {env_prod_file} not found.")