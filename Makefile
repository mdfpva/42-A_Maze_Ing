MAIN = a_maze_ing.py
PYTHON = python3
CONFIG = config.txt
MODULE = mazegen/
TESTS = tests/
VENV = .venv

all: run

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

run: install
	clear
	$(VENV)/bin/$(PYTHON)  $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	rm -rf **/__pycache__ .mypy_cache .pytest_cache
	find . -name "*.pyc" -delete

fclean: clean
	rm -rf $(VENV) 

re: fclean run

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy $(MAIN) $(MODULE) $(TESTS) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy $(MAIN) $(MODULE) $(TESTS) --strict

test:
	./$(VENV)/bin/$(PYTHON) -m pytest -v

.PHONY: all install run clean fclean re lint lint-strict test debug
