## NOTE: Lots of files in various subdirectories have the same name (such as
## "LICENSE") so this short macro allows us to distinguish them by using their
## directory names (from the source tree) as prefixes for the files.
%global add_to_license_files() \
        mkdir -p _license_files ; \
cp -p %1 _license_files/$(echo '%1' | sed -e 's!/!.!g')

Name:           wpewebkit
Version:        2.21.92
Release:        4%{?dist}
Summary:        A WebKit port optimized for low-end devices

License:        LGPLv2 and BSD
URL:            http://www.%{name}.org/
Source0:        http://wpewebkit.org/releases/%{name}-%{version}.tar.xz

# https://bugs.webkit.org/show_bug.cgi?id=158785
Patch0:     fedora-crypto-policy.patch
# Explicitly specify python2 over python to avoid build fails
Patch1:     python2.patch
#https://bugs.webkit.org/show_bug.cgi?id=189078
Patch2:     webkit-jsc-use-ternary-operator.patch
#https://bugs.webkit.org/show_bug.cgi?id=189556
Patch3:     epoxy.patch
#https://bugs.webkit.org/show_bug.cgi?id=189797
Patch4:     static-tooling.patch

BuildRequires:  bison
BuildRequires:  cairo-devel
BuildRequires:  cmake
BuildRequires:  libwpe-devel
BuildRequires:  wpebackend-fdo-devel
BuildRequires:  flex
BuildRequires:  gcc-c++
BuildRequires:  gnutls-devel
BuildRequires:  gperf
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  gstreamer1-plugins-bad-free-devel
BuildRequires:  harfbuzz-devel
BuildRequires:  libicu-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  libsoup-devel
BuildRequires:  libwebp-devel
BuildRequires:  libxslt-devel
BuildRequires:  libwayland-client-devel
BuildRequires:  libwayland-egl-devel
BuildRequires:  libwayland-server-devel
BuildRequires:  mesa-libgbm-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  perl-File-Copy-Recursive
BuildRequires:  perl-JSON-PP
BuildRequires:  perl-Switch
BuildRequires:  python2
BuildRequires:  ruby
BuildRequires:  rubygems
BuildRequires:  sqlite-devel
BuildRequires:  woff2-devel
BuildRequires:  libepoxy-devel

%description
WPE allows embedders to create simple and performant systems based on
Web platform technologies. It is designed with hardware acceleration
in mind, leveraging common 3D graphics APIs for best performance.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries, build data, and header
files for developing applications that use %{name}

%prep
%autosetup -p1 -n wpewebkit-%{version}

%build
# Increase the DIE limit so our debuginfo packages could be size optimized.
# Decreases the size for x86_64 from ~5G to ~1.1G.
# https://bugzilla.redhat.com/show_bug.cgi?id=1456261
%global _dwz_max_die_limit 250000000

# The _dwz_max_die_limit is being overridden by the arch specific ones from the
# redhat-rpm-config so we need to set the arch specific ones as well - now it
# is only needed for x86_64.
%global _dwz_max_die_limit_x86_64 250000000

%ifarch s390 aarch64
# Use linker flags to reduce memory consumption - on other arches the ld.gold is
# used and also it doesn't have the --reduce-memory-overheads option
%global optflags %{optflags} -Wl,--no-keep-memory -Wl,--reduce-memory-overheads
%endif

# Decrease debuginfo even on ix86 because of:
# https://bugs.webkit.org/show_bug.cgi?id=140176
%ifarch s390 s390x %{arm} %{ix86} ppc %{power64} %{mips}
# Decrease debuginfo verbosity to reduce memory consumption even more
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')
%endif

%ifarch ppc
# Use linker flag -relax to get WebKit build under ppc(32) with JIT disabled
%global optflags %{optflags} -Wl,-relax
%endif

# Disable ld.gold on s390 as it does not have it.
# Also for aarch64 as the support is in upstream, but not packaged in Fedora.
# FIXME: Ideally the CMAKE_EXE_LINKER_FLAGS would not be necessary, but builds seem to be failing otherwise.
mkdir -p %{_target_platform}
pushd %{_target_platform}
%cmake \
  -DPORT=WPE \
  -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_MINIBROWSER=ON \
%ifarch s390 aarch64
  -DUSE_LD_GOLD=OFF \
%endif
%ifarch s390 s390x ppc %{power64}
  -DENABLE_JIT=OFF \
  -DUSE_SYSTEM_MALLOC=ON \
%endif
..
popd

%make_build -C %{_target_platform}

%install
%make_install -C %{_target_platform}

# Finally, copy over and rename various files for %license inclusion
%add_to_license_files Source/JavaScriptCore/COPYING.LIB
%add_to_license_files Source/JavaScriptCore/icu/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/common/third_party/smhasher/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/compiler/LICENSE
%add_to_license_files Source/ThirdParty/ANGLE/src/third_party/libXNVCtrl/LICENSE
%add_to_license_files Source/WebCore/icu/LICENSE
%add_to_license_files Source/WebCore/LICENSE-APPLE
%add_to_license_files Source/WebCore/LICENSE-LGPL-2
%add_to_license_files Source/WebCore/LICENSE-LGPL-2.1
%add_to_license_files Source/WebInspectorUI/UserInterface/External/CodeMirror/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/ESLint/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/Esprima/LICENSE
%add_to_license_files Source/WebInspectorUI/UserInterface/External/three.js/LICENSE
%add_to_license_files Source/WTF/icu/LICENSE
%add_to_license_files Source/WTF/wtf/dtoa/COPYING
%add_to_license_files Source/WTF/wtf/dtoa/LICENSE

%files
%{_bindir}/WPEWebDriver
%{_libdir}/libWPEWebKit-0.1.so.2
%{_libdir}/libWPEWebKit-0.1.so.2.*
%{_libexecdir}/wpe-webkit-0.1
%{_libdir}/wpe-webkit-0.1
%doc NEWS
%license _license_files/*ThirdParty*
%license _license_files/*WebCore*
%license _license_files/*WebInspectorUI*
%license _license_files/*WTF*
%license _license_files/*JavaScriptCore*

%files devel
%{_includedir}/wpe-webkit-0.1
%{_libdir}/libWPEWebKit-0.1.so
%{_libdir}/pkgconfig/*.pc


%changelog
* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.21.92-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jan 24 2019 Pete Walter <pwalter@fedoraproject.org> - 2.21.92-3
- Rebuild for ICU 63

* Fri Sep 21 2018 Chris King <bunnyapocalypse@protonmail.org> - 2.21.92-2
- Adding another patch so the package properly installs

* Fri Sep 14 2018 Chris King <bunnyapocalypse@protonmail.org> - 2.21.92-1
- Adding some patches to fix failing builds

* Mon Sep 10 2018 Chris King <bunnyapocalypse@protonmail.org> - 2.21.92-1
- Soname bump and version update

* Tue Jul 17 2018 Chris King <bunnyapocalypse@fedoraproject.org> - 2.21.2-1
- Initial RPM package.
