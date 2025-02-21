import secrets


{{ cookiecutter.update({"secret_key": secrets.token_urlsafe(32)}) }}
{{ cookiecutter.update({"token_secret_key": secrets.token_urlsafe(32)}) }}
