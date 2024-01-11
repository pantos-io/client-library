.PHONY: dist
dist: wheel

.PHONY: code
code: check format lint sort bandit test

.PHONY: check
check:
	mypy pantos/client/library

.PHONY: sort
sort:
	isort --force-single-line-imports pantos/client/library tests

.PHONY: test
test:
	python3 -m pytest tests

.PHONY: coverage
coverage:
	python3 -m pytest --cov-report term-missing --cov=pantos tests
	rm .coverage

.PHONY: bandit
bandit:
	bandit -r pantos/client/library tests --quiet --configfile=.bandit

.PHONY: lint
lint:
	flake8 pantos/client/library tests

.PHONY: format
format:
	yapf --in-place --recursive pantos/client/library tests

.PHONY: wheel
wheel: dist/pantos_client_library-$(PANTOS_CLIENT_LIBRARY_VERSION)-py3-none-any.whl

dist/pantos_client_library-$(PANTOS_CLIENT_LIBRARY_VERSION)-py3-none-any.whl: environment-variables pantos/ pantos-client-library.conf.$(PANTOS_CLIENT_LIBRARY_ENVIRONMENT) setup.py submodules/common/pantos/common/
	cp pantos-client-library.conf.$(PANTOS_CLIENT_LIBRARY_ENVIRONMENT) pantos/pantos-client-library.conf
	python3 setup.py bdist_wheel
	rm pantos/pantos-client-library.conf

.PHONY: install
install: environment-variables dist/pantos_client_library-$(PANTOS_CLIENT_LIBRARY_VERSION)-py3-none-any.whl
	python3 -m pip install dist/pantos_client_library-$(PANTOS_CLIENT_LIBRARY_VERSION)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	python3 -m pip uninstall -y pantos-client-library

.PHONY: clean
clean:
	rm -r -f build/
	rm -r -f dist/
	rm -r -f pantos_client_library.egg-info/

.PHONY: environment-variables
environment-variables:
ifndef PANTOS_CLIENT_LIBRARY_ENVIRONMENT
	$(error PANTOS_CLIENT_LIBRARY_ENVIRONMENT is undefined)
endif
ifndef PANTOS_CLIENT_LIBRARY_VERSION
	$(error PANTOS_CLIENT_LIBRARY_VERSION is undefined)
endif
