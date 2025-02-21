import secrets

# Generar claves seguras
def generate_secret_key():
    return secrets.token_urlsafe(32)

# Asignar las claves generadas a los valores del contexto de Cookiecutter
context = {
    "secret_key": generate_secret_key(),
    "token_secret_key": generate_secret_key()
}

# Actualizar el contexto global de Cookiecutter
def update_cookiecutter_context(context):
    for key, value in context.items():
        globals()["cookiecutter"][key] = value

update_cookiecutter_context(context)
