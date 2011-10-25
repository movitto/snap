export PYTHON = python
export PYTHONPATH='.'
export HELP2MAN=help2man

all:
	$(PYTHON) bin/setup.py build

man:
	PYTHONPATH=$(PYTHONPATH) $(HELP2MAN) -N -o docs/man1/snap.man bin/snaptool

install:
	$(PYTHON) bin/setup.py install
	cp docs/man1/snap.man /usr/share/man/man1/

clean:
	rm -rfv build
	rm -fv snap/*.pyc
	rm -fv packagesystems/*.pyc

distclean: clean

