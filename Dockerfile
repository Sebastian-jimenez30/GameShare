FROM python:3.11

# Evita que Python guarde archivos .pyc y loguee en buffer
ENV PYTHONUNBUFFERED=1

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

COPY . /code

# Expone el puerto por donde correrá el servidor
EXPOSE 80

# Comando por defecto para desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
