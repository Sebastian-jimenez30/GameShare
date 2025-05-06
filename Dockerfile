# Usa una imagen base de Python 3.11 con herramientas mínimas
FROM python:3.11-slim

# Evita que Python guarde archivos .pyc y loguee en buffer
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Establece el directorio de trabajo
WORKDIR /code

# Instala dependencias del sistema necesarias para compilaciones, gettext y tailwind
RUN apt-get update && apt-get install -y \
    gettext \
    build-essential \
    curl \
    npm \
    nodejs \
    && apt-get clean

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copia el resto del código al contenedor
COPY . .

# Expone el puerto por donde correrá el servidor
EXPOSE 8000

# Comando por defecto para desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
