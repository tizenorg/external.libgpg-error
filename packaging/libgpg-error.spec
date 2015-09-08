Summary: Library for error values used by GnuPG components 
Name: libgpg-error
Version: 1.7
Release: 1
URL: ftp://ftp.gnupg.org/gcrypt/libgpg-error/
Source0: ftp://ftp.gnupg.org/gcrypt/libgpg-error/%{name}-%{version}.tar.bz2
Source1001: %{name}.manifest
Group: System/Libraries
License: LGPL-2.1+ and GPL-2.0+
BuildRequires: gawk, gettext-tools
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
This is a library that defines common error values for all GnuPG
components.  Among these are GPG, GPGSM, GPGME, GPG-Agent, libgcrypt,
pinentry, SmartCard Daemon and possibly more in the future.

%package devel
Summary: Development files for the %{name} package
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
This is a library that defines common error values for all GnuPG
components.  Among these are GPG, GPGSM, GPGME, GPG-Agent, libgcrypt,
pinentry, SmartCard Daemon and possibly more in the future. This package
contains files necessary to develop applications using libgpg-error.

%prep
%setup -q
# The config script already suppresses the -L if it's /usr/lib, so cheat and
# set it to a value which we know will be suppressed.
sed -i -e 's|^libdir=@libdir@$|libdir=@exec_prefix@/lib|g' src/gpg-error-config.in
cp %{SOURCE1001} .

%build
%configure --disable-static --enable-malloc0returnsnull
make

%install
rm -fr $RPM_BUILD_ROOT
mkdir -p %{buildroot}/usr/share/license
cp %{_builddir}/%{name}-%{version}/COPYING %{buildroot}/usr/share/license/%{name}
cat %{_builddir}/%{name}-%{version}/COPYING.LIB >> %{buildroot}/usr/share/license/%{name}

%make_install
rm -rf $RPM_BUILD_ROOT/%{_datadir}/common-lisp

%find_lang %{name}

# Relocate the shared libraries to /%{_lib}.
mkdir -p $RPM_BUILD_ROOT/%{_lib}
for shlib in $RPM_BUILD_ROOT/%{_libdir}/*.so* ; do
	if test -L "$shlib" ; then
		rm "$shlib"
	else
		mv "$shlib" $RPM_BUILD_ROOT/%{_lib}/
	fi
done
# Figure out where /%{_lib} is relative to %{_libdir}.
touch $RPM_BUILD_ROOT/root_marker
relroot=..
while ! test -f $RPM_BUILD_ROOT/%{_libdir}/$relroot/root_marker ; do
	relroot=$relroot/..
done
# Overwrite development symlinks.
pushd $RPM_BUILD_ROOT/%{_libdir}
for shlib in $relroot/%{_lib}/lib*.so.* ; do
	shlib=`echo "$shlib" | sed -e 's,//,/,g'`
	target=`basename "$shlib" | sed -e 's,\.so.*,,g'`.so
	ln -sf $shlib $target
done
popd
# Add the soname symlink.
/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_lib}/
rm -f $RPM_BUILD_ROOT/root_marker

%check
make check

%clean
rm -fr $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -f %{name}.lang
%manifest %{name}.manifest
/usr/share/license/%{name}
%defattr(-,root,root)
%{_bindir}/gpg-error
/%{_lib}/libgpg-error.so.*

%files devel
%defattr(-,root,root)
%{_bindir}/gpg-error-config
%{_libdir}/libgpg-error.so
%{_includedir}/gpg-error.h
%{_datadir}/aclocal/gpg-error.m4

