fix:
	python -m black .
	python -m isort .

mypy:
	python -m mypy .

pylint:
	python -m pylint api_crawler.py common.py web_crawler.py
