
PYTHON_FILES = \
    src/circuitpainter/__init__.py \
    src/circuitpainter/circuitpainter.py

lint:
	autopep8 --in-place --max-line-length 80 --aggressive --aggressive  ${PYTHON_FILES}
	mypy --ignore-missing-imports ${PYTHON_FILES}
	pylint --max-line-length 80 ${PYTHON_FILES}
