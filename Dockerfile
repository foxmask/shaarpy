# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

RUN apt-get update -q && apt-get install -qy pandoc\
    && rm -rf /var/lib/apt/lists/*

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install pip requirements
COPY requirements.txt .
COPY requirements-conf-server.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app
