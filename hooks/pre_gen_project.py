import secrets


def generate_secret_key():
    return secrets.token_urlsafe(32)

cookiecutter.update({
    "secret_key": generate_secret_key(),
    "token_secret_key": generate_secret_key()
})

