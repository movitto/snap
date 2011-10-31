export VERSION=0.5
export PYTHON = python
export PYDOC  = pydoc
export PYTHONPATH='.'
export HELP2MAN=help2man

all:
	$(PYTHON) setup.py build

doc:
	test -d docs/api || mkdir docs/api
	cd docs/api/ ; $(PYDOC) -w ../../

man:
	PYTHONPATH=$(PYTHONPATH) $(HELP2MAN) -N -o docs/man1/snap.man bin/snaptool

install:
	$(PYTHON) setup.py install --root=$(DESTDIR)
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
	rpmbuild -ba snap.spec

deb: clean
	debuild -us -uc

distclean: clean

