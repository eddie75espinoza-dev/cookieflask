# {{ cookiecutter.project_name }}

![Static Badge](https://img.shields.io/badge/Estatus-En%20Desarrollo-yellow)
![Static Badge](https://img.shields.io/badge/Versi%C3%B3n-1.0.0-blue)
![Static Badge](https://img.shields.io/badge/Lenguaje-Python-blue)
![Static Badge](https://img.shields.io/badge/Pruebas-En%20Desarrollo-yellow)

## **Descripción General**

{{ cookiecutter.project_short_description }}

## Índice

* [Requisitos de Instalación](#requisitos-de-instalación)
* [Guía de Configuración](#guía-de-configuración)
* [Descripción de Endpoints](#descripción-de-endpoints)
* [Logs y Monitoreo](#logs-y-monitoreo)
* [Contribución](#contribución)
* [Pruebas](#pruebas)

## Requisitos de Instalación

Para ejecutar **{{ cookiecutter.project_name }}**, necesitas tener instalados los siguientes programas:

### Instalación de Docker
- [Docker](https://docs.docker.com/get-docker/): Para gestionar contenedores.

### Instalación de Docker Compose
- [Docker-compose](https://docs.docker.com/compose/install/): Para definir y ejecutar aplicaciones multi-contenedor.

## Guía de Configuración

### Configurar el archivo .env

Ver archivo `.env.example` para configuraciones detalladas.

### Construir y Levantar los Contenedores

Dada la separación de los ambientes de desarrollo y producción, ejecute los siguientes comandos para construir y levantar los contenedores:

#### Contenedor en ambiente de producción
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

#### Contenedor en ambiente de desarrollo
```bash
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d --build
```

Para detener el servicio, ejecutar el siguiente comando en la terminal:

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod down -v
```

## Descripción de Endpoints

La documentación completa de los endpoints está disponible en:
- Desarrollo: `http://localhost:5000/docs`
- Ver también: [backend/docs/documentation.md](/backend/docs/documentation.md)

## Logs y Monitoreo

Los logs de la aplicación se encuentran en:
- Contenedor: `/backend/logs/`

## Contribución

1. Fork el repositorio
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Pruebas

Para verificar el correcto funcionamiento del servicio web, ejecute el siguiente comando en la terminal mientras el contenedor Docker esté activo:

```bash
docker exec -it {{cookiecutter.docker_image_backend}} pytest
```

Para ejecutar los tests con cobertura, usar estos comandos:
Para ver la cobertura básica:
```bash
# Ejecutar tests para middleware
docker exec -it {{cookiecutter.docker_image_backend}} pytest --cov=core.middleware
```

Para ver cobertura detallada con líneas faltantes:
```bash
# Ejecutar con líneas no cubiertas en los tests
docker exec -it {{cookiecutter.docker_image_backend}} pytest --cov=core.middleware --cov-report=term-missing
```

Para ver solo los archivos específicos:
```bash
docker exec -it {{cookiecutter.docker_image_backend}} pytest tests/jwt_middleware_test.py --cov=core.middleware --cov-report=term-missing
```

Para generar reporte HTML (más detallado):
```bash
docker exec -it {{cookiecutter.docker_image_backend}} pytest --cov=core.middleware --cov-report=html:htmlcov
```

Para verificar que alcances el 90% mínimo:
```bash
docker exec -it {{cookiecutter.docker_image_backend}} pytest --cov=core.middleware --cov-report=term-missing --cov-fail-under=90
```

El reporte te mostrará:

Porcentaje de cobertura total
Líneas específicas no cubiertas por tests
Si falla cuando no alcanza el 90%

El reporte HTML, podrá abrirse desde htmlcov/index.html, use un navegador para ver un reporte visual detallado de qué líneas están cubiertas y cuáles no.