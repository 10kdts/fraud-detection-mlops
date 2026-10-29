.PHONY: data train test api all
data:
	python -m src.fraudml.generate
train:
	python -m src.fraudml.model
test:
	python -m unittest discover -s tests -v
api:
	python -m src.fraudml.api
all: data train test

