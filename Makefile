export PYTHON = python

all:
	$(PYTHON) bin/setup.py build

install:
	$(PYTHON) bin/setup.py install
	cp docs/man1/snap.man /usr/share/man/man1/

clean:
	rm -rfv build
	rm -fv snap/*.pyc
	rm -fv packagesystems/*.pyc

distclean: clean

