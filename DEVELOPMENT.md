# Project development

## Testing examples:

This just runs the examples; it doesn't verify their outputs

    cd examples
    python3 -m venv --system-site-packages .venv
    . .venv/bin/activate
    pip install -e ../
    python *.py
    rm *.kicad*
    deactivate

## Linting

    python3 -m venv .venv
    . .venv/bin/activate
    pip install autopep8 mypy pylint numpy

    make lint

## Publishing to PyPi

This library is published using flit.

Before publishing, be sure to lint the code, and update the version number
in src/circuitpainter/__init__.py

First, make a virtual environment to publish from:

    python3 -m venv .venv
    . .venv/bin/activate
    pip install flit

Next, build the project using flit, then upload it:

    flit build
    flit publish

Finally, the virtual enviroment can be removed:

    deactivate
    rm -rf .venv

