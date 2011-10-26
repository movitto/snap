export VERSION=0.5
export PYTHON = python
export PYTHONPATH='.'
export HELP2MAN=help2man

all:
	$(PYTHON) bin/setup.py build

man:
	PYTHONPATH=$(PYTHONPATH) $(HELP2MAN) -N -o docs/man1/snap.man bin/snaptool

install:
	$(PYTHON) bin/setup.py install --root=$(DESTDIR)
	cp docs/man1/snap.man $(DESTDIR)/usr/share/man/man1/

clean:
	rm -rfv build
	rm -fv snap/*.pyc
	rm -fv snap/metadata/*.pyc
	rm -fv snap/backends/*.pyc
	rm -fv snap/backends/*/*.pyc

package:
	tar czvf build/snap-${VERSION}.tgz . --exclude=.git --transform='s,./,snap-$(VERSION)/,'

rpm: package
	cp build/snap-$(VERSION).tgz ~/rpmbuild/SOURCES
	rpmbuild -ba contrib/fedora/snap.spec

distclean: clean

