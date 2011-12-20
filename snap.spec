# these don't seem to be defined on f16+
%global _icons16dir    %{_datadir}/icons/hicolor/16x16/apps
%global _icons22dir    %{_datadir}/icons/hicolor/22x22/apps
%global _icons24dir    %{_datadir}/icons/hicolor/24x24/apps
%global _icons32dir    %{_datadir}/icons/hicolor/32x32/apps
%global _icons48dir    %{_datadir}/icons/hicolor/48x48/apps
%global _iconsscaldir  %{_datadir}/icons/hicolor/scalable/apps

Name:         snap
Version:      0.6
Release:      1%{?dist}
Summary:      A modular system backup/restore utility

Group:       Applications/System
License:     GPLv3
URL:         http://projects.morsi.org/snap
Source0:     http://mo.morsi.org/files/snap/snap-0.6.tgz

BuildArch:      noarch
BuildRequires:  desktop-file-utils
%if 0%{?with_python3}
BuildRequires:  python3-devel
%else
BuildRequires:  python2-devel
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
%if 0%{?with_python3}
Requires: pygobject3
%else
Requires: pygobject2
%endif

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
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1  \
         $RPM_BUILD_ROOT%{_iconsscaldir} \
         $RPM_BUILD_ROOT%{_icons16dir}   \
         $RPM_BUILD_ROOT%{_icons22dir}   \
         $RPM_BUILD_ROOT%{_icons24dir}   \
         $RPM_BUILD_ROOT%{_icons32dir}   \
         $RPM_BUILD_ROOT%{_icons48dir}   \
         $RPM_BUILD_ROOT%{_datadir}/pixmaps
make install DESTDIR=$RPM_BUILD_ROOT
desktop-file-install --dir=$RPM_BUILD_ROOT%{_datadir}/applications resources/snap.desktop
cp resources/gsnap.svg    $RPM_BUILD_ROOT/%{_iconsscaldir}/gsnap.svg
cp resources/gsnap-16.png $RPM_BUILD_ROOT/%{_icons16dir}/gsnap.png
cp resources/gsnap-22.png $RPM_BUILD_ROOT/%{_icons22dir}/gsnap.png
cp resources/gsnap-24.png $RPM_BUILD_ROOT/%{_icons24dir}/gsnap.png
cp resources/gsnap-32.png $RPM_BUILD_ROOT/%{_icons32dir}/gsnap.png
cp resources/gsnap-48.png $RPM_BUILD_ROOT/%{_icons48dir}/gsnap.png
cp resources/gsnap-16.png $RPM_BUILD_ROOT/%{_datadir}/pixmaps/gsnap.png

pushd $RPM_BUILD_ROOT/%{_mandir}/man1
ln -s snap.1.gz snaptool.1.gz

%files
%{python_sitelib}/snap/
%{_bindir}/snaptool
%config(noreplace) %{_sysconfdir}/snap.conf
%{_datadir}/snap
%{_mandir}/man1/snap.1.gz
%{_mandir}/man1/snaptool.1.gz
%{python_sitelib}/snap*.egg-info
%doc CHANGELOG LICENSE README

%files gtk
%{_bindir}/gsnap
%{_datadir}/applications/snap.desktop
%{_datadir}/pixmaps/gsnap.png
%{_iconsscaldir}/gsnap.svg
%{_icons16dir}/gsnap.png
%{_icons22dir}/gsnap.png
%{_icons24dir}/gsnap.png
%{_icons32dir}/gsnap.png
%{_icons48dir}/gsnap.png

%changelog
* Mon Dec 19 2011 Mo Morsi <mo@morsi.org> 0.6-1
- new upstream release

* Sat Dec 10 2011 Mo Morsi <mo@morsi.org> 0.5-8
- include additional sized icons
- include pixmap file

* Thu Dec 08 2011 Mo Morsi <mo@morsi.org> 0.5-7
- more updates to conform to fedora guidelines
- conditionalize python2/3-devel dependency
- include upstream fix in release tarball

* Thu Dec 08 2011 Mo Morsi <mo@morsi.org> 0.5-6
- more updates to conform to fedora guidelines
- include docs in files section

* Wed Dec 07 2011 Mo Morsi <mo@morsi.org> 0.5-5
- more updates to conform to fedora guidelines
- source0 now matches upstream release
- fix long lines, shorted symbollic links,
  conditionalize pygobject2/3 dependency

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
