#!/bin/sh -e

find . | grep -E "(__pycache__|\.pyc|\.pyo|\.pytest_cache|\.tox|\.eml|\.mypy_cache$)" | xargs rm -rf
