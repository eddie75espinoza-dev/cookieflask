# Plantilla Flask con Cookiecutter

Este repositorio contiene una plantilla para iniciar proyectos basados en Flask utilizando Cookiecutter. Con esta plantilla, podrás generar rápidamente la estructura básica de un proyecto Flask, siguiendo buenas prácticas y una organización modular.

## Características

- Estructura organizada: La plantilla genera un directorio principal con el nombre definido por `{{cookiecutter.project_name}}`, dentro del cual se encuentra el subdirectorio backend que aloja los archivos centrales de la aplicación.

- Hooks personalizados: Se incluye un hook (/hooks/post_gen_project.py) que permite ejecutar tareas adicionales tras la generación del proyecto.

- Configuración flexible: Personaliza tu proyecto mediante el archivo cookiecutter.json, definiendo variables y opciones según tus necesidades.

## Requisitos

- Cookiecutter (versión >= 2.6.0)

    Puedes instalarlo utilizando pip:

  ```bash
  pip install cookiecutter
  ```  
- Python 3.x

## Descargar la Plantilla

Puedes descargar la última versión de esta plantilla de dos formas:

1. Descarga directa:

    Descarga el archivo ZIP de la última versión:

    Descargar plantilla_flask.zip

    https://github.com/usuario_github/cookieflask/archive/refs/heads/main.zip


2. Clonando el repositorio:

    ```bash
    git clone https://github.com/usuario_github/cookieflask.git
    ```
Una vez clonado, puedes generar tu proyecto ejecutando:

```bash
cookiecutter ./plantilla_flask
```

## Uso

Para generar un nuevo proyecto basado en esta plantilla, ejecuta:

```bash
cookiecutter https://github.com/usuario_github/cookieflask.git
```
Si tienes el repositorio clonado localmente:

```bash
cookiecutter /ruta/a/plantilla_flask
```

Durante la ejecución, se te solicitarán valores para las variables definidas en cookiecutter.json (por ejemplo, project_name), permitiéndote personalizar el proyecto generado.

## Estructura del Proyecto Generado

Una vez generado el proyecto, la estructura será similar a la siguiente:

```bash
{{cookiecutter.project_name}}/
├── backend/
│   ├── app.py           # Archivo principal de la aplicación Flask
│   ├── requirements.txt # Dependencias del proyecto
│   ├── Dockerfile       # Dockerfile del proyecto
│   └── ...              # Otros módulos y archivos del proyecto
├── docker-compose.yml   # Contenedores del proyecto
└── README.md            # Documentación del proyecto
```
> Nota: La estructura puede variar según las opciones configuradas en cookiecutter.json.

## Hooks

El directorio `/hooks` contiene scripts que se ejecutan durante el proceso de generación del proyecto. En particular, post_gen_project.py se ejecuta al finalizar la creación del proyecto y puede utilizarse para:

- Inicializar un repositorio Git.
- Configurar variables de entorno.
- Realizar otras tareas de personalización.

Si deseas modificar el comportamiento de estos hooks, puedes editar directamente los scripts ubicados en el directorio /hooks.


### Notas finales

Una vez concluida la descarga de la plantilla vaya al archivo `.gitignore` y descomente las lineas referentes a los archivos `_.env_` y `_.vscode_` esto evitará que sea incluyan en los 'commits' posteriores en su trabajo con el repositorio.
Una vez generadas las API KEY elimine el archivo `_keygen.py_`.