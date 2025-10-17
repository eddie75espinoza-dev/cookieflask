import os
import re
import sys
import secrets
import shutil


def generate_secret_key():
    return secrets.token_urlsafe(32)

use_db = "{{cookiecutter.use_db}}"
env_file = os.path.join(os.getcwd(), '.env')


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
    secret_key = generate_secret_key()
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as file:
            content = file.read()
        
        secret_key_pattern = r'^SECRET_KEY=.*$'
        
        if re.search(secret_key_pattern, content, re.MULTILINE):
            # Reemplazar la línea existente
            new_content = re.sub(secret_key_pattern, f'SECRET_KEY={secret_key}', content, flags=re.MULTILINE)
            with open(env_file, 'w') as file:
                file.write(new_content)
            print(f"✅ Secret key updated in {env_file}")
        else:
            # No existe, agregar al final
            with open(env_file, 'a') as file:
                file.write(f"\nSECRET_KEY={secret_key}\n")
            print(f"✅ Secret key added to {env_file}")


write_secret_key(env_file)
print(f"💻 All set! Let's start coding! 🔥")