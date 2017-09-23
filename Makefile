NAME = $(shell python setup.py --name)
FULLNAME = $(shell python setup.py --fullname)
DESCRIPTION = $(shell python setup.py --description)
VERSION = $(shell python setup.py --version)
URL = $(shell python setup.py --url)

DOCS_DIR = docs

.PHONY: clean help install coverage docs doc-html doc-pdf dev-install quality release test tox

help:
	@echo '$(NAME) - $(DESCRIPTION)'
	@echo 'Version: $(VERSION)'
	@echo 'URL: $(URL)'
	@echo
	@echo 'Targets:'
	@echo '  help         : display this help text.'
	@echo '  install      : install package $(NAME).'
	@echo '  test         : run all tests.'
	@echo '  tox          : run all tests with tox.'
	@echo '  docs         : generate documentation files.'
	@echo '  clean        : remove files created by other targets.'

install:
	python setup.py install

dev-install:
	pip install -r dev-requirements.txt
	pip install -e .

docs: doc-html

doc-html: test
	cd $(DOCS_DIR); $(MAKE) html

release: test docs
	python setup.py sdist --formats=gztar
	@echo "Uploading to PyPI."
	twine upload dist/tryme-$(VERSION).*
	@echo "Done."

test:
	tox

clean:
	cd $(DOCS_DIR) && $(MAKE) clean
	rm -rf build/ dist/ *.egg-info MANIFEST $(DOCS_DIR)/conf.pyc *~
