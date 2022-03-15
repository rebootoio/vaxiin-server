help:       ## show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

run:        ## Run application
	. ./venv/bin/activate && \
	pip install -r requirements.txt && \
	APP_LOG_LEVEL=DEBUG APP_ENV=development python app/vaxiin_server.py

test:        ## test application
	. ./venv/bin/activate && \
	python -m pytest --disable-warnings

build:      ## build application
	docker build -t vaxiin-server .
