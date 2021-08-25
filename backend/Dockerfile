FROM python:3.9.4-alpine
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/
RUN apk update \
	&& apk add --no-cache --virtual build-deps build-base libffi-dev mariadb-dev jpeg-dev zlib-dev libjpeg \
	&& pip install -r requirements.txt
	#&& apk del build-deps
COPY . /code/

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
