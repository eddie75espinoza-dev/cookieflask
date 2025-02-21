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

new_secret_key = generate_secret_key()

{% if cookiecutter.secret_key == "_secret_key_to_replace_" %}
{{ cookiecutter.update({ "secret_key": new_secret_key }) }}
{% endif %}