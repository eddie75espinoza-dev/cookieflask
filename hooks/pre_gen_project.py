import secrets


def generate_secret_key():
    return secrets.token_urlsafe(32)

secret_key = generate_secret_key()
token_secret_key = generate_secret_key()

{{ cookiecutter.update({"secret_key": secret_key}) }}
{{ cookiecutter.update({"token_secret_key": token_secret_key}) }}

print(secret_key)
print(token_secret_key)