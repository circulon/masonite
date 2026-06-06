init:
	cp .env-example .env
	pip install --upgrade pip
	pip install -e '.[test,dev]'
	# Create MySQL Database
	# Create Postgres Database
test:
	python -m pytest tests
ci:
	cp .env-example .env
	python -m pip install --upgrade pip
	pip install -e '.[test]'
ci-test:
	python -m pytest tests -m "not integrations"
lint:
	python -m flake8 src/masonite/ --ignore=E501,F401,E203,E128,E402,E731,F821,E712,W503,F811
format:
	black src/masonite
	black tests/
	make lint
sort:
	isort tests
	isort src/masonite
coverage:
	python -m pytest --cov-report term --cov-report xml --cov=src/masonite tests/
	python -m coveralls
show:
	python -m pytest --cov-report term --cov-report html --cov=src/masonite tests/
cov:
	python -m pytest --cov-report term --cov-report xml --cov=src/masonite tests/
build:
	python -m pip install --upgrade build
	python -m build
clean:
	rm -rf build dist src/*.egg-info
