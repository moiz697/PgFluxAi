# Makefile
.PHONY: install build clean test

install:
	python3 -m pip install --upgrade pip setuptools wheel
	python3 -m pip install -r requirements.txt

build:
	python3 -m build

clean:
	rm -rf dist
	rm -rf src/pgflux.egg-info
	rm -rf __pycache__
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

test:
	python3 -m unittest discover -s src/pgflux/tests -p 'test_*.py'
