import os
import sys
import secrets
import shutil


def generate_secret_key():
    return secrets.token_urlsafe(32)

use_db = "{{cookiecutter.use_db}}"
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


def write_secret_key(env_file):
    if os.path.exists(env_file):
        with open(env_file, 'a') as file:
            file.write(f"\nSECRET_KEY={generate_secret_key()}\n")
        print(f"✅ Secret keys updated in {env_file}")
    else:
        print(f"⚠️ File {env_file} not found.")


write_secret_key(env_dev_file)
write_secret_key(env_prod_file)

print(f"💻 All set! Let's start coding! 🔥")