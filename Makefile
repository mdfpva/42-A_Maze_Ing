MAIN = a_maze_ing.py
PYTHON = python3
CONFIG = config.txt
MODULE = mazegen/
TESTS = tests/
VENV = .venv

all: $(VENV) install run

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

run:
	clear
	$(VENV)/bin/$(PYTHON)  $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf **/__pycache__ .mypy_cache .pytest_cache
	find . -name "*.pyc" -delete

fclean: clean
	rm -rf $(VENV) build dist mazegen.egg-info

re: fclean run

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy $(MAIN) $(MODULE) $(TESTS) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy $(MAIN) $(MODULE) $(TESTS) --strict

test:
	./$(VENV)/bin/$(PYTHON) -m pytest -v

build: $(VENV) mazegen
	.venv/bin/pip install build
	.venv/bin/python3 -m build --wheel
	cp dist/mazegen-1.0.0-py3-none-any.whl .
	ls *.whl

.PHONY: all install run clean fclean re lint lint-strict test debug build
