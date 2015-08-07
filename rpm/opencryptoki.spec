Name: opencryptoki
Version: 3.3+git1.594702a
Release: 1
Summary: TPM and softtoken interface for PKCS#11
Group: System/Base
License: CPL
Source0: %{name}-%{version}.tar.gz
URL: http://sourceforge.net/projects/opencryptoki/
BuildRequires: pkgconfig(libcrypto)
BuildRequires: trousers-devel
BuildRequires: pkgconfig(systemd)
BuildRequires: automake bison flex
BuildRequires: libtool
Requires(pre): shadow-utils
Requires(pre): /usr/bin/groupadd-user
Requires(postun): shadow-utils
%systemd_requires

%description
%{summary}.

%files
%defattr(-,root,root,-)
%{_sysconfdir}/ld.so.conf.d/*.conf
%{_sysconfdir}/pkcs11/modules/%{name}.module
%dir %{_sysconfdir}/%{name}
%config %{_sysconfdir}/%{name}/%{name}.conf
%{_sbindir}/pkcs*
%{_libdir}/%{name}/*.so*
%{_libdir}/%{name}/methods
%{_libdir}/%{name}/stdll/*_sw.so*
%{_libdir}/pkcs11/*.so*
%{_libdir}/pkcs11/methods
%{_libdir}/pkcs11/stdll
%{_unitdir}/*.service
%{_tmpfilesdir}/*.conf
%dir %attr(770,root,pkcs11) %{_localstatedir}/lib/%{name}
%dir %attr(770,root,pkcs11) %{_localstatedir}/lib/%{name}/swtok
%dir %attr(770,root,pkcs11) %{_localstatedir}/lib/%{name}/swtok/TOK_OBJ



%package devel
Summary: Development files for %{name}
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
%{summary}.

%files devel
%defattr(-,root,root,-)
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h



%package tpm
Summary: TPM token support for %{name}
Group: System/Base
Requires: %{name} = %{version}-%{release}

%description tpm
%{summary}.

%files tpm
%defattr(-,root,root,-)
%{_libdir}/%{name}/stdll/*_tpm.so*
%dir %attr(770,root,pkcs11) %{_localstatedir}/lib/%{name}/tpm


%package doc
Summary: Documentation for %{name}
Group: Documentation

%description doc
%{summary}.

%files doc
%defattr(-,root,root,-)
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man7/*
%{_mandir}/man8/*


%prep
%setup -q -n %{name}-%{version}/%{name}


%build
autoreconf -vfi
%configure \
    --disable-icatok \
    --disable-ccatok \
    --enable-swtok \
    --disable-ep11tok \
    --enable-tpmtok \
    --disable-iscftok \
    --with-systemd=%{_unitdir}
make %{?_smp_mflags}


%install
make DESTDIR=%{buildroot} install
rm %{buildroot}/%{_libdir}/pkcs11/PKCS11_*
rm %{buildroot}/%{_libdir}/%{name}/*.la
rm %{buildroot}/%{_libdir}/%{name}/PKCS11_*
rm %{buildroot}/%{_libdir}/%{name}/stdll/PKCS11_*
rm %{buildroot}/%{_libdir}/%{name}/stdll/*.la

mkdir -p %{buildroot}/%{_sysconfdir}/pkcs11/modules
cat <<EOF > %{buildroot}/%{_sysconfdir}/pkcs11/modules/%{name}.module
module: %{_libdir}/pkcs11/libopencryptoki.so
critical: no
EOF

mkdir -p %{buildroot}/%{_tmpfilesdir}
cat <<EOF > %{buildroot}/%{_tmpfilesdir}/%{name}.conf
D /run/lock/opencryptoki 0770 root pkcs11
D /run/lock/opencryptoki/swtok 0770 root pkcs11
D /run/lock/opencryptoki/tpm 0770 root pkcs11
EOF


%pre
groupadd -rf pkcs11

%preun
%{systemd_preun pkcsslotd.service}

%post
/sbin/ldconfig
%{?tmpfiles_create:%tmpfiles_create %{_tmpfilesdir}/opencryptoki.conf}
%{systemd_post pkcsslotd.service}

%postun
%{systemd_postun pkcsslotd.service}
/sbin/ldconfig
if [ "$1" == 0 ]; then
  getent group pkcs11 >/dev/null && groupdel pkcs11
fi
