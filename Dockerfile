# Usar la imagen base de Python en Alpine
FROM python:3.10-alpine

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para Flet y Python
RUN apk add --no-cache \
    gcc \
    g++ \
    libffi-dev \
    musl-dev \
    python3-dev \
    make \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxrandr-dev \
    libxcursor-dev \
    libxi-dev \
    libxtst-dev \
    libxinerama-dev

# Copiar los archivos de la aplicación al contenedor
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar la aplicación
CMD ["python", "-m", "pchat", "-s", "true"]
