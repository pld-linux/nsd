##
##  nsd.spec -- OpenPKG RPM Specification
##  Copyright (c) 2000-2003 Cable & Wireless Deutschland GmbH
##  Copyright (c) 2000-2003 The OpenPKG Project <http://www.openpkg.org/>
##  Copyright (c) 2000-2003 Ralf S. Engelschall <rse@engelschall.com>
##
##  Permission to use, copy, modify, and distribute this software for
##  any purpose with or without fee is hereby granted, provided that
##  the above copyright notice and this permission notice appear in all
##  copies.
##
##  THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
##  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
##  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
##  IN NO EVENT SHALL THE AUTHORS AND COPYRIGHT HOLDERS AND THEIR
##  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
##  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
##  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
##  USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
##  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
##  OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
##  SUCH DAMAGE.
##

#   FIXME rse: optional AXFR support via BIND8 named-xfer?
#   FIXME rse: optional libwrap support via {tcp,socket}_wrappers for AXFR

Name:		nsd
Summary:	Name Server Daemon
URL:		http://www.nlnetlabs.nl/nsd/
Vendor:		NLNet Labs
Group:		Daemons
License:	GPL
Version:	1.0.2
Release:	0.1
Source0:	http://www.nlnetlabs.nl/downloads/nsd/%{name}-%{version}.tar.gz
# Source0-md5:	8c50f242ed4d71986fe8959f5db3be5d
Source1:	rc.%{name}
Source2:	%{name}.zones
Source3:	%{name}c.conf
Source4:	example.com
Source5:	fsl.%{name}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildPreReq:	OpenPKG, openpkg >= 20030103, fsl, make
PreReq:		OpenPKG, openpkg >= 20030103, fsl
AutoReq:	no
AutoReqProv:	no

%description
NSD is an authoritative only, high performance, simple name server. It
is especially intended to be run as a root nameserver and actually is
used for the Internet K-Root-Server driven by RIPE NCC. It supports
BIND-style zone files, but pre-compiles the DNS RRs into packet format
in a separate step.

%prep
%setup -q

%build
#   build programs
%{l_make} %{l_mflags -O} \
	CC="%{l_cc}" \
	CFLAGS="%{l_cflags -O}" \
	NSDUSER="%{l_ruid}.%{l_rgid}" \
	NAMEDXFER="%{l_prefix}/libexec/bind/named-xfer" \
	NSDKEYSDIR="%{l_prefix}%{_sysconfdir}/nsd/keys" \
	PREFIX="%{l_prefix}" \
	NSDZONESDIR="%{l_prefix}%{_sysconfdir}/nsd" \
	NSDZONES="%{l_prefix}%{_sysconfdir}/nsd/nsd.zones" \
	NSDDB="%{l_prefix}/var/nsd/nsd.db" \
	NSDPIDFILE="%{l_prefix}/var/nsd/nsd.pid" \
	FEATURES="-DLOG_NOTIFIES -DBIND8_STATS" \
	LIBWRAP="`%{l_prefix}/bin/fsl-config --all --ldflags --libs`"

%install
rm -rf $RPM_BUILD_ROOT

#   pre-create installation hierarchy
%{l_shtool} mkdir -f -p -m 755 \
	$RPM_BUILD_ROOT%{l_prefix}/etc/rc.d \
	$RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/fsl \
	$RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/nsd/nsd.db \
	$RPM_BUILD_ROOT%{l_prefix}/sbin \
	$RPM_BUILD_ROOT%{l_prefix}/man/man8 \
	$RPM_BUILD_ROOT%{l_prefix}/var/nsd

#   perform default installation procedure
%{l_make} %{l_mflags} install \
	PREFIX="$RPM_BUILD_ROOT%{l_prefix}" \
	NSDZONESDIR="$RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/nsd" \
	NSDZONES="$RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/nsd/nsd.zones" \
	NSDDB="$RPM_BUILD_ROOT%{l_prefix}/var/nsd/nsd.db" \
	NSDPIDFILE="$RPM_BUILD_ROOT%{l_prefix}/var/nsd/nsd.pid" \
	INSTALL="%{l_shtool} install -c"

#   install default configuration
%{l_shtool} install -c -m 644 \
	%{SOURCE nsdc.conf} $RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/nsd/
%{l_shtool} install -c -m 644 \
	%{SOURCE nsd.zones} $RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/nsd/
%{l_shtool} install -c -m 644 \
	%{SOURCE example.com} $RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/nsd/nsd.db/

#   install run-command script
%{l_shtool} install -c -m 755 \
	-e 's;@l_prefix@;%{l_prefix};g' \
	-e 's;@l_susr@;%{l_susr};g' \
	%{SOURCE rc.nsd} $RPM_BUILD_ROOT%{l_prefix}/etc/rc.d/

#   install fsl configuration file
%{l_shtool} install -c -m 644 \
	-e 's;@l_prefix@;%{l_prefix};g' \
	%{SOURCE fsl.nsd} $RPM_BUILD_ROOT%{l_prefix}%{_sysconfdir}/fsl/

#   strip installation
strip $RPM_BUILD_ROOT%{l_prefix}/sbin/* >/dev/null 2>&1 || true

#   determine installation files
%{l_rpmtool} files -v -ofiles -r$RPM_BUILD_ROOT \
	%{l_files_std} \
	'%not %dir %{l_prefix}/etc/rc.d' \
	'%not %dir %{l_prefix}%{_sysconfdir}/fsl' \
	'%attr(755,%{l_rusr},%{l_rgrp}) %{l_prefix}/var/nsd'

%files -f files
%defattr(644,root,root,755)

%clean
rm -rf $RPM_BUILD_ROOT

%post
#   update database
%{l_prefix}/sbin/nsdc rebuild
