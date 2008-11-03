Summary:	Database Firewall
Name:		greensql-fw
Version:	0.9.4
Release:	%mkrel 2
License:	GPL
Group:		System/Servers
URL:		http://sourceforge.net/projects/greensql/
Source0:	http://dfn.dl.sourceforge.net/sourceforge/greensql/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Patch0:		greensql-fw-logdir.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:	libevent-devel
BuildRequires:	mysql-devel
BuildRequires:	pcre-devel
BuildRequires:	flex
BuildRequires:	bison
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
GreenSQL is a database firewall engine used to protect Open Source Databases
from SQL injection attacks. It works in proxy mode. Application logics is based
on evaluating of SQL commands using risk score factors, as well as blocking of
sensitive commands.

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1

cp %{SOURCE1} %{name}.init
cp %{SOURCE2} %{name}.sysconfig
cp %{SOURCE3} %{name}.logrotate

# fix attribs
find -type f | xargs chmod 644

%build
%serverbuild

make CXXFLAGS="$CXXFLAGS `mysql_config --include` -Wall -D_REENTRANT"

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/greensql
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}/var/log/greensql


install -m0755 src/%{name} %{buildroot}%{_sbindir}/%{name}

install -m0644 conf/greensql.conf %{buildroot}%{_sysconfdir}/greensql/
install -m0644 conf/mysql.conf %{buildroot}%{_sysconfdir}/greensql/

install -m0755 %{name}.init %{buildroot}%{_initrddir}/%{name}
install -m0644 %{name}.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
install -m0644 %{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
if [ "$1" -ge "1" ]; then
    %{_initrddir}/%{name} condrestart > /dev/null 2>&1 ||:
fi	

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%doc db docs scripts license.txt mem-test.sh readme.txt
%dir %{_sysconfdir}/greensql
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/greensql/greensql.conf
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/greensql/mysql.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_initrddir}/%{name}
%{_sbindir}/%{name}
%dir /var/log/greensql
