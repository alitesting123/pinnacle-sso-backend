.PHONY: help install dev test lint format clean

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean up"

install:
	pip install -r requirements.txt

dev:
	python app/main.py

test:
	pytest -v

lint:
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
