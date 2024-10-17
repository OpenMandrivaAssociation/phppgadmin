%define rname phpPgAdmin

Summary:	PostgreSQL database adminstration over the web interface
Name:		phppgadmin
Version:	5.1
Release:	2
License:	GPLv2+
Group:		System/Servers
URL:		https://sourceforge.net/projects/phppgadmin
Source0:	http://prdownloads.sourceforge.net/phppgadmin/%{rname}-%{version}.tar.bz2
Patch0:		phpPgAdmin-4.1.1-mdv_conf.diff
Requires:	apache-mod_php
Requires:	php-pgsql
Requires:	php-gettext
BuildRequires:	imagemagick
BuildRequires:	pkgconfig(jasper)
BuildRequires:	recode
BuildArch:	noarch

%description
phpPgAdmin is phpMyAdmin (for MySQL) ported to PostgreSQL.
phpPgAdmin is a fully functional PostgreSQL administration
utility. You can use it to  create and maintain multiple databases
and even multiple servers.

%prep
%setup -q -n %{rname}-%{version}
%patch0 -p0

# clean up CVS stuff
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
	if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

%build

%install
export DONT_RELINK=1

install -d %{buildroot}%{_webappconfdir}
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}/var/www/%{name}

cp -aRf * %{buildroot}/var/www/%{name}/

mv %{buildroot}/var/www/%{name}/conf/config.inc.php-dist %{buildroot}%{_sysconfdir}/%{name}/config.inc.php
rm -rf %{buildroot}/var/www/%{name}/conf

# generate UTF-8 files
pushd lang
#	make DESTDIR=./recoded
popd
install -m0644 lang/*.php  %{buildroot}/var/www/%{name}/lang/

# cleanup
pushd %{buildroot}/var/www/%{name}
	rm -rf sql
	rm -f CREDITS DEVELOPERS FAQ HISTORY INSTALL LICENSE TODO TRANSLATORS
	rm -f lang/Makefile lang/convert.awk lang/php2po lang/po2php lang/synch lang/langcheck
popd

cat > %{buildroot}%{_webappconfdir}/%{name}.conf << EOF
Alias /%{name} /var/www/%{name}

<Directory /var/www/%{name}>
	Require local granted
	ErrorDocument 403 "Access denied per %{_webappconfdir}/%{name}.conf"
</Directory>
EOF

# fix dir perms
find %{buildroot} -type d | xargs chmod 755

# fix file perms
find %{buildroot} -type f | xargs chmod 644

# Mandriva Icons
install -d %{buildroot}%{_iconsdir}
install -d %{buildroot}%{_miconsdir}
install -d %{buildroot}%{_liconsdir}

convert images/themes/default/title.png -resize 16x16  %{buildroot}%{_miconsdir}/%{name}.png
convert images/themes/default/title.png -resize 32x32  %{buildroot}%{_iconsdir}/%{name}.png
convert images/themes/default/title.png -resize 48x48  %{buildroot}%{_liconsdir}/%{name}.png


# XDG menu
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=phpPgAdmin
Name[ru]=phpPgAdmin
Comment=phpPgAdmin is a web administration GUI for PostgreSQL.
Comment[ru]=Администрирование PostgreSQL через Web-интерфейс.
Exec=%{_bindir}/www-browser http://localhost/%{name}/
Icon=%{name}
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Databases;
EOF

%files
%doc CREDITS DEVELOPERS FAQ HISTORY INSTALL LICENSE TODO TRANSLATORS plugins/Report/sql/reports-pgsql.sql
%config(noreplace) %{_webappconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%attr(0640,apache,root) %config(noreplace) %{_sysconfdir}/%{name}/config.inc.php
/var/www/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop


