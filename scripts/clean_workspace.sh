#!/bin/sh -e

find . | grep -E "(__pycache__|\.pyc|\.pyo|\.pytest_cache|\.tox|\.mypy_cache$)" | xargs rm -rf
