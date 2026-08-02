MAIN = a_maze_ing.py
PYTHON = python3
CONFIG = config.txt
MODULE = mazegen/
VENV = .venv

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

run: install
	$(VENV)/bin/$(PYTHON)  $(MAIN) $(CONFIG)

all: run

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -name "*.pyc" -delete

fclean: clean
	rm -rf $(VENV) 

re: fclean run

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy $(MAIN) $(MODULE) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy $(MAIN) $(MODULE) --strict

test:
	./$(VENV)/bin/$(PYTHON) -m pytest -v

.PHONY: all install run clean fclean re lint lint-strict test debug
