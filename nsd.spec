# TODO: deal with "nsd" user, make init script
Summary:	Name Server Daemon
Summary(pl.UTF-8):   Serwer DNS (Name Server Daemon)
Name:		nsd
Version:	2.2.1
Release:	0.1
License:	BSD
Group:		Networking/Daemons
Source0:	http://www.nlnetlabs.nl/downloads/nsd/%{name}-%{version}.tar.gz
# Source0-md5:	6875cb2495122654334e6234ebeb9d98
URL:		http://www.nlnetlabs.nl/nsd/
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel
#BuildRequires:	rpmbuild(macros) >= 1.202
#Requires(post,preun):	/sbin/chkconfig
#Requires(postun):	/usr/sbin/userdel
#Requires(pre):	/bin/id
#Requires(pre):	/usr/sbin/useradd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/nsd

%description
NSD is an authoritative only, high performance, simple and open source
name server. It is especially intended to be run as a root nameserver
and actually is used for the Internet K-Root-Server driven by RIPE
NCC. It supports BIND-style zone files, but pre-compiles the DNS RRs
into packet format in a separate step.

%description -l pl.UTF-8
NSD jest wysokowydajnym, prostym, wolnodostępnym serwerem DNS,
udzielającym wyłącznie autorytatywnych odpowiedzi. Jest on
przeznaczony głównie do działania jako serwer domeny głównej,
aktualnie wykorzystywany przez RIPE NCC jako K-Root-Server Internetu.
Wspiera on pliki stref w stylu BINDa, ale zawarte w nich rekordy DNS
są w osobnym kroku prekompilowane do formatu pakietowego.

%prep
%setup -q

%build
%configure \
	--enable-ipv6 \
	--enable-plugins \
	--enable-bind8-stats \
	--with-libwrap

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	sbindir=$RPM_BUILD_ROOT%{_sbindir} \
	configdir=$RPM_BUILD_ROOT%{_sysconfdir} \
	mandir=$RPM_BUILD_ROOT%{_mandir} \
	configfile=$RPM_BUILD_ROOT%{_sysconfdir}/nsdc.conf \
	zonesfile=$RPM_BUILD_ROOT%{_sysconfdir}/nsd.zones

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/nsdc.conf{.sample,}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/nsd.zones{.sample,}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# useradd nsd

%post
# chkconfig --add
%{_sbindir}/nsdc rebuild

%preun
# chkconfig --del

%postun
# userdel nsd

%files
%defattr(644,root,root,755)
%doc CREDITS DIFFERENCES README RELNOTES REQUIREMENTS TODO contrib/build*
%attr(755,root,root) %{_sbindir}/*
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nsdc.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/nsd.zones
%{_mandir}/man8/*
