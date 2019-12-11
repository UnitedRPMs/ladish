%filter_from_requires /.*libalsapid.so*/d
%filter_setup

%global commit0 5fe205f2dc5931854a1126ca50bf682eca959430
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

Name:          ladish
Summary:       LADI Audio session handler
Version:       2
Release:       21%{?gver}%{dist}
License:       GPLv2+
Group:         Applications/Multimedia
URL:           http://ladish.org/

Source0:       https://github.com/LADI/ladish/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

# clean up desktop files
Patch0:        ladish-1-desktop.patch
# NOTE - this will be need to reviewed each version release due to 
# non numeric version number in wscript
Patch1:        handle-aarch64.patch

Patch2:        adab42244350e2d57784743ea1ac286ce76ed3cd.patch
Patch3:        57e8a93ae048dc460b6a4d0e8237768b5ef1d45e.patch

Requires:      laditools
Requires:      pygtk2
Requires:      dbus
BuildRequires: pkgconfig(python3)
BuildRequires: desktop-file-utils
BuildRequires: jack-audio-connection-kit-devel
BuildRequires: alsa-lib-devel
BuildRequires: libuuid-devel
BuildRequires: dbus-devel
BuildRequires: expat-devel
BuildRequires: gtk2-devel
BuildRequires: dbus-glib-devel
BuildRequires: boost-devel
BuildRequires: flowcanvas-devel
BuildRequires: pygtk2-devel
BuildRequires: python3-pyyaml
BuildRequires: gcc-c++

%description
Session management system for JACK applications on GNU/Linux. Its aim
is to have many different audio programs running at once, to save their
setup, close them down and then easily reload the setup at some other
time. ladish doesn't deal with any kind of audio or MIDI data itself;
it just runs programs, deals with saving/loading (arbitrary) data and
connects JACK ports together.
Ladish has a GUI frontend called gladish, based on lpatchage (LADI Patchage)
and the ladish_control command line app for headless operation.

%package -n gladish
Summary:    GTK ladish front end
Requires:   %{name}%{_isa} = %{version}-%{release}

%description -n gladish
A suite of tools to configure and control the Jack Audio Connection Kit.
Laditools contains laditray, a tray icon control tool for Jack D-Bus.
This package is mandatory for installing the LADI Audio Session Handler.

%prep
%autosetup -n %{name}-%{commit0} -p1

# remove bundled libs
sed -i -e "s|'-fvisibility=hidden')|\['-fvisibility=hidden'\]+'%{optflags} -fno-tree-pta'.split(' '))|"\
       -e "s|\['PREFIX'\]), 'lib')|\['PREFIX'\]), '%{_libdir}')|" wscript
# gcc7 throws warnings on glibmm-2.4 headers. The -Werror turns these into errors.
# This can be removed if/when there is an update on the glibmm-2.4 package:
sed -i "/add_cflag(conf, '-Werror')/d" wscript
# move preloaded lib out of LD path
sed -i -e "s|libalsapid.so|%{_libdir}\/ladish\/libalsapid.so|" daemon/loader.c

# Python2 fixes (nop, python3 isn't ready)
sed -i 's|/usr/bin/env python|/usr/bin/python2|g' $PWD/waf
sed -i 's|/usr/bin/env python|/usr/bin/python2|g' $PWD/ladish_control
sed -i 's|/usr/bin/env python|/usr/bin/python2|g' $PWD/wscript

%build

# Python2 fixes (nop, python3 isn't ready)
find -depth -type f -writable -name "*.py" -exec sed -iE '1s=^#! */usr/bin/\(python\|env python\)[23]\?=#!%{__python2}=' {} +

/usr/bin/python2 ./waf configure --prefix=%{_prefix} -v
LIBDIR=%{_libdir} CFLAGS="%{optflags} -fno-tree-pta" CXXFLAGS="%{optflags} -fno-tree-pta" ./waf -v

%install
/usr/bin/python2 ./waf install --destdir=%{buildroot}
# move lib out of LDPATH
mkdir  %{buildroot}/%{_libdir}/%{name}
mv %{buildroot}%{_libdir}/libalsapid.so   %{buildroot}/%{_libdir}/%{name}/

sed -i 's|/usr/bin/env python|/usr/bin/python2|g' %{buildroot}/%{_bindir}/ladish_control

%find_lang %{name}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/gladish.desktop || :

%files -f %{name}.lang
%doc README AUTHORS COPYING NEWS
%{_bindir}/ladishd
%{_bindir}/jmcore
%{_bindir}/ladiconfd
%{_bindir}/ladish_control
%{_libdir}/%{name}
%{_datadir}/%{name}
%{_datadir}/dbus-1/services/org.%{name}.service
%{_datadir}/dbus-1/services/org.%{name}.conf.service
%{_datadir}/dbus-1/services/org.%{name}.jmcore.service

%files -n gladish
%{_datadir}/applications/gladish.desktop
%{_bindir}/gladish
%{_datadir}/icons/hicolor/*/apps/gladish.png

%changelog

* Tue Dec 10 2019 David Va <davidva AT tuta DOT io> - 2-21.git5fe205f
- Not a movie, contrary to popular opinion. The magic is here!

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2-20.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 11 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2-19.3.gitfcb16ae
- Remove obsolete scriptlets

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2-18.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2-17.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jul 07 2017 Igor Gnatenko <ignatenko@redhat.com> - 2-16.3.gitfcb16ae
- Rebuild due to bug in RPM (RHBZ #1468476)

* Wed Feb 15 2017 Orcan Ogetbil <oget [dot] fedora [at] gmail [dot] com> - 2-15.3.gitfcb16ae
- Removed -Werror from the build flags (due to stringent gcc7 warnings)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2-14.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2-13.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 21 2016 Jonathan Wakely <jwakely@redhat.com> - 2-12.3.gitfcb16ae
- Rebuilt for Boost 1.60

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 2-11.3.gitfcb16ae
- Rebuilt for Boost 1.59

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2-10.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 2-9.3.gitfcb16ae
- rebuild for Boost 1.58

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2-8.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 2-7.3.gitfcb16ae
- Rebuilt for GCC 5 C++11 ABI change

* Tue Jan 27 2015 Petr Machata <pmachata@redhat.com> - 2-6.3.gitfcb16ae
- Rebuild for boost 1.57.0

* Tue Sep 09 2014 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 2-5.3.gitfcb16ae
- handle AArch64 in same way as lot of other architectures

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2-4.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2-3.3.gitfcb16ae
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 2-2.3.gitfcb16ae
- Rebuild for boost 1.55.0

* Thu Oct 10 2013 Brendan Jones <brendan.jones.it@gmail.com> 2-1.3.gitfcb16ae
- Filter libalsapid.so from requires

* Tue Oct 08 2013 Brendan Jones <brendan.jones.it@gmail.com> 2-1.2.gitfcb16ae
- Hardcode libalsapid.so location 
- add BR dbus
- validate desktop file

* Fri Jun 28 2013 Brendan Jones <brendan.jones.it@gmail.com> 2-1.1.gitfcb16ae
- Update to latest git

* Sun Oct 28 2012 Brendan Jones <brendan.jones.it@gmail.com> 2-0.3.git2c3c3f0
- Move private library out of LDPATH

* Fri Oct 12 2012 Brendan Jones <brendan.jones.it@gmail.com> 2-0.2.git2c3c3f0
- Update git revision

* Sun Jun 03 2012 Brendan Jones <brendan.jones.it@gmail.com> 2-0.1.git49eca11
- Update to latest git snapshot

* Tue Mar 06 2012 Brendan Jones <brendan.jones.it@gmail.com> 1-1
- initial build
