install:
		poetry install

build:
		./build.sh

dev:
		poetry run flask --app page_analyzer:app run

mydev:
		poetry run flask --app page_analyzer:app run --debug --host=172.18.167.62

lint:
		poetry run flake8 page_analyzer

test-coverage:
		poetry run pytest --cov=gendiff tests --cov-report xml

PORT ?= 8000
start:
		poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app