.PHONY: all test clean
all test clean:

venv:
	python -m venv venv
	. venv/bin/activate; \
	pip install -U pip pip-tools

requirements.txt: requirements.in venv
	. venv/bin/activate; \
	python -m piptools compile requirements.in --output-file $@

requirements-dev.txt: requirements-dev.in requirements.txt
	. venv/bin/activate; \
	python -m piptools compile requirements.txt requirements-dev.in --output-file $@

.PHONY: install
install: requirements-dev.txt
	. venv/bin/activate; \
	python -m piptools sync $<; \
	pre-commit install

.PHONY: lint
lint:
	. venv/bin/activate; \
	python -m pre_commit run --all-files --show-diff-on-failure
	. venv/bin/activate; \
	mypy .
