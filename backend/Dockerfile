FROM python:3.9.4-alpine
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False

WORKDIR /code
COPY requirements.txt /code/
RUN apk update \
	&& apk add --no-cache --virtual build-deps build-base libffi-dev jpeg-dev zlib-dev libjpeg \
	&& apk add cairo cairo-tools pango-dev gdk-pixbuf fontconfig ttf-opensans mariadb-dev \
	&& pip install -r requirements.txt \
	&& apk del build-deps
COPY . /code/

RUN mkdir -p /code/db/
RUN mkdir -p ${HOME}/.fonts/

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
