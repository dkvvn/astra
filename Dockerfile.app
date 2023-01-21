FROM python:3.10.9-slim

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /astra
RUN chown -R $USER:$USER /astra && chmod 755 /astra
USER $USER

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Установка зависимостей в порядке их записи
COPY requirements_app.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    cat requirements_app.txt | xargs -n 1 pip install
    
COPY . .

