%define _requires_exceptions pear(/usr/share/smarty/Smarty.class.php)

Summary:	Database Firewall
Name:		greensql-fw
Version:	1.3.0
Release:	%mkrel 1
License:	GPL
Group:		System/Servers
URL:		http://www.greensql.net/
#Source0:	http://www.greensql.net/download/get?os=Source_Code&platform=Any&filename=greensql-fw-%{version}.tar.gz
Source0:	greensql-fw-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Patch0:		greensql-fw-logdir.diff
Patch1:		greensql-console-mdv_conf.diff
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

%package -n	greensql-console
Summary:	Manages a GreenSQL Database Firewall
Group:		System/Servers
Requires(post): rpm-helper
Requires(postun): rpm-helper
Requires:	apache-mod_php php-mysql
Requires:	php-smarty >= 2.3.0
BuildRequires:	apache-base >= 2.0.54
Suggests:	greensql-fw
Suggests:	mysql

%description -n	greensql-console
The greensql-console package is web management tool used to manage GreenSQL
Database Firewall.

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1

cp %{SOURCE1} %{name}.init
cp %{SOURCE2} %{name}.sysconfig
cp %{SOURCE3} %{name}.logrotate

# fix attribs
find -type d | xargs chmod 755
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

install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
install -d %{buildroot}%{_sysconfdir}/greensql-console
install -d %{buildroot}/var/www/greensql-console
install -d %{buildroot}/var/lib/greensql-console/smarty/templates_c

cp -aRf greensql-console/* %{buildroot}/var/www/greensql-console/

mv %{buildroot}/var/www/greensql-console/config.php %{buildroot}%{_sysconfdir}/greensql-console/config.php

cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/greensql-console.conf << EOF

Alias /greensql-console /var/www/greensql-console

<Directory /var/www/greensql-console>
    Order Deny,Allow
    Deny from All
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/greensql-console.conf"
</Directory>
EOF

# cleanup
rm -rf %{buildroot}/var/www/greensql-console/configs
rm -rf %{buildroot}/var/www/greensql-console/libs
#rm -rf %{buildroot}/var/www/%{name}/templates
rm -rf %{buildroot}/var/www/greensql-console/templates_c

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
if [ "$1" -ge "1" ]; then
    %{_initrddir}/%{name} condrestart > /dev/null 2>&1 ||:
fi

%post -n greensql-console
%_post_webapp

%postun -n greensql-console
%_postun_webapp

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

%files -n greensql-console
%defattr(0644,root,root,0755)
%doc license.txt readme.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/greensql-console.conf
%attr(0700,apache,apache) %dir %{_sysconfdir}/greensql-console
%attr(0640,apache,apache) %config(noreplace) %{_sysconfdir}/greensql-console/config.php
/var/www/greensql-console
%attr(0700,apache,apache) %dir /var/lib/greensql-console
%attr(0700,apache,apache) %dir /var/lib/greensql-console/smarty
%attr(0700,apache,apache) %dir /var/lib/greensql-console/smarty/templates_c
