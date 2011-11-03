Name:	      snap	
Version:    0.5	
Release:	  1%{?dist}
Summary:	  A modular system backup/restore utility which uses the native package management system

Group:		  Applications/System
License:	  GPLv3
URL:		    http://projects.morsi.org/snap
Source0:	  http://mo.morsi.org/files/snap/snap-0.5.tgz

BuildArch:      noarch
BuildRequires:	python2-devel
%if 0%{?with_python3}
BuildRequires:  python3-devel
%endif # if with_python3
Requires:  python-crypto

%description
Snap! is a system snapshot utility which uses the underlying package
management system and native tooling to take and restore system snapshots.

It provides a very simple command line and graphical interface as well as
an API which can be easily extended to take snapshots of any custom system
entity (support for repositories, packages, files, and various services are
provided right out of the box)

%prep
%setup -q

%build
make %{?_smp_mflags}

# due to how snap works this currently needs to be run as sudo / root
#%check
#%{__python} test/run.py

%install
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
make install DESTDIR=$RPM_BUILD_ROOT

%files
%{python_sitelib}/snap/
%{_bindir}/snaptool
%{_bindir}/gsnap
%{_sysconfdir}/snap.conf
%{_datadir}/snap
%{_mandir}/man1/snap.man.gz
%{python_sitelib}/snap*.egg-info

%changelog
* Tue Oct 25 2011 Mo Morsi <mo@morsi.org> 0.5-1
- Initial package
