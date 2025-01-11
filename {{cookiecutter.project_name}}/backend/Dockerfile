FROM python:{{ cookiecutter.python_version }}-slim

# PYTHONDONTWRITEBYTECODE:
# Evita archivos innecesarios (.pyc).
# Reduce el tamaño de la imagen y mantiene el contenedor limpio.
ENV PYTHONDONTWRITEBYTECODE 1
# PYTHONUNBUFFERED:
# Logs en tiempo real.
# Mejora la depuración y el monitoreo.
ENV PYTHONUNBUFFERED 1

WORKDIR /backend

RUN apt-get update && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --upgrade pip setuptools && \
  pip install --no-cache-dir -r requirements.txt

COPY . ./

CMD ["gunicorn", "app:app", "workers", "4", "--host", "0.0.0.0", "--port", "5000"]