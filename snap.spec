# these don't seem to be defined on f16+
%global _icons48dir    %{_datadir}/icons/hicolor/48x48/apps
%global _iconsscaldir  %{_datadir}/icons/hicolor/scalable/apps

Name:         snap
Version:      0.5
Release:      4%{?dist}
Summary:      A modular system backup/restore utility

Group:       Applications/System
License:     GPLv3
URL:         http://projects.morsi.org/snap
Source0:     http://mo.morsi.org/files/snap/snap-0.5.tgz

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  desktop-file-utils
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

%package gtk
Summary: Snap! GUI interface
Group:   Applications/System
License: GPLv3
Requires: %{name} = %{version}-%{release}
Requires: pygtk2
Requires: pygobject3

%description gtk
Provides gsnap a GTK frontend to the Snap! system snapshotter

%prep
%setup -q

%build
make %{?_smp_mflags}

# due to how snap works this currently needs to be run as sudo / root
#%%check
#%%{__python} test/run.py

%install
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1 $RPM_BUILD_ROOT%{_iconsscaldir} $RPM_BUILD_ROOT%{_icons48dir}
make install DESTDIR=$RPM_BUILD_ROOT
desktop-file-install --dir=$RPM_BUILD_ROOT%{_datadir}/applications resources/snap.desktop
cp resources/gsnap.svg    $RPM_BUILD_ROOT/%{_iconsscaldir}/gsnap.svg
cp resources/gsnap-48.png $RPM_BUILD_ROOT/%{_icons48dir}/gsnap.png
ln -s %{_mandir}/man1/snap.1.gz $RPM_BUILD_ROOT/%{_mandir}/man1/snaptool.1.gz

%files
%{python_sitelib}/snap/
%{_bindir}/snaptool
%config(noreplace) %{_sysconfdir}/snap.conf
%{_datadir}/snap
%{_mandir}/man1/snap.1.gz
%{_mandir}/man1/snaptool.1.gz
%{python_sitelib}/snap*.egg-info

%files gtk
%{_bindir}/gsnap
%{_datadir}/applications/snap.desktop
%{_iconsscaldir}/gsnap.svg
%{_icons48dir}/gsnap.png

%changelog
* Tue Nov 22 2011 Mo Morsi <mo@morsi.org> 0.5-4
- add missing pyobject3 dependency
- added 48x48 icon and icon macros for F16+

* Tue Nov 22 2011 Mo Morsi <mo@morsi.org> 0.5-3
- More updates to conform to Fedora guidelines
- add desktop file and icon, reduce line lengths,
- escape macros in comments, make config file as such,
- added missing dependencies
- create gtk subpackage

* Tue Nov 22 2011 Mo Morsi <mo@morsi.org> 0.5-2
- Updates to conform to Fedora guidelines
- remove tabs in spec, rename snap.man to snap.1

* Tue Oct 25 2011 Mo Morsi <mo@morsi.org> 0.5-1
- Initial package
