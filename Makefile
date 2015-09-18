run:
	PYTHONPATH=src python -m mixup docs/db-sample.txt

clean:
	find . -name '*.pyc' -delete
