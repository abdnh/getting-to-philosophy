fix:
	python -m pylint api_crawler.py common.py web_crawler.py
	python -m black .

mypy:
	python -m mypy .

