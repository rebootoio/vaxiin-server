help:        ## show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

run:         ## Run application
	. ./venv/bin/activate && \
	pip install -r requirements.txt && \
	APP_LOG_LEVEL=DEBUG APP_ENV=development python app/vaxiin_server.py

test:        ## test application
	. ./venv/bin/activate && \
	pip install -r test-requirements.txt && \
	python -m pytest --disable-warnings

coverage:    ## get test coverage report
	. ./venv/bin/activate && \
	pip install -r test-requirements.txt && \
	coverage run -m pytest --disable-warnings && \
	coverage report -m --omit=app/handler/*,app/exceptions/handler.py

test_docker: ## test application in docker
	docker build -f Dockerfile.tests --tag vaxiin-server-tests . && \
	docker run --rm vaxiin-server-tests

build:       ## build application
	docker build -t vaxiin-server .
