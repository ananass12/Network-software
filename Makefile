WEEK ?= 01

.PHONY: test


test:
	python3 -m pytest -q weeks/week-$(WEEK)/tests
