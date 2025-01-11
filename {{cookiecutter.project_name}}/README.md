# {{ cookiecutter.project_name }}

![Static Badge](https://img.shields.io/badge/Estatus-En%20Desarrollo-yellow)
![Static Badge](https://img.shields.io/badge/Versi%C3%B3n-1.0.0-blue)
![Static Badge](https://img.shields.io/badge/Lenguaje-Python-blue)
![Static Badge](https://img.shields.io/badge/Pruebas-En%20Desarrollo-yellow)

## **Descripción General**

{{ cookiecutter.short_description_project }}

## Índice

* [Requisitos de Instalación](#requisitos-de-instalación)
* [Guía de Configuración](#guía-de-configuración)
* [Descripción de Endpoints](#descripción-de-endpoints)
* [Pruebas](#pruebas)

## Requisitos de Instalación

Para ejecutar **{{ cookiecutter.project_name }}**, necesitas tener instalados los siguientes programas:

### Instalación de Docker
- [Docker](https://docs.docker.com/get-docker/): Para gestionar contenedores.

### Instalación de Docker Compose
- [Docker-compose](https://docs.docker.com/compose/install/): Para definir y ejecutar aplicaciones multi-contenedor.

## Guía de Configuración

### Configurar el archivo .env

Crea un archivo _.env_ en la base del proyecto con las siguientes variables

```bash
# AMBIENTE DE LA APLICACIÓN (elegir una opción)
ENVIRONMENT=<'production', 'development', 'staging'>

HOST={{ cookiecutter.host }}
PORT={{ cookiecutter.port }}
BASE_URL={{ cookiecutter.base_url }} # Para producción

# DB
POSTGRES_USER=<postgres_user>
POSTGRES_PASSWORD=<postgres_password>
POSTGRES_HOST=<postgres_host>
POSTGRES_PORT=<postgres_port>
POSTGRES_DB=<postgres_db>
```

### Construir y Levantar los Contenedores

Ejecuta los siguientes comandos para construir y levantar los contenedores:

```bash
docker-compose build
docker-compose up -d
```
Para detener el servicio, ejecutar el siguiente comando en la terminal:

```bash
docker-compose down -v
```

## Descripción de Endpoints


## Pruebas

Para verificar el correcto funcionamiento del servicio web, ejecute el siguiente comando en la terminal mientras el contenedor Docker esté activo:

```bash
docker exec -it {{cookiecutter.docker_image_backend}} pytest
```