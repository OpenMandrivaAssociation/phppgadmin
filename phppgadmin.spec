%define rname phpPgAdmin

Summary:        Intended to handle the adminstration of PostgreSQL over the web
Name:           phppgadmin
Version:        4.2.2
Release:        %mkrel 4
License:        GPL
Group:          System/Servers
URL:            http://sourceforge.net/projects/phppgadmin
Source0:        http://prdownloads.sourceforge.net/phppgadmin/%{rname}-%{version}.tar.bz2
Patch0:         phpPgAdmin-4.1.1-mdv_conf.diff
Requires:  apache-mod_php
Requires:  php-pgsql
Requires:  php-gettext
Requires(post): ccp >= 0.4.0
%if %mdkversion < 201010
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
%endif
BuildRequires:  ImageMagick
BuildRequires:  libjasper
BuildRequires:  recode
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

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
rm -rf %{buildroot}

export DONT_RELINK=1

install -d %{buildroot}%{webappconfdir}
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}/var/www/%{name}

cp -aRf * %{buildroot}/var/www/%{name}/

mv %{buildroot}/var/www/%{name}/conf/config.inc.php-dist %{buildroot}%{_sysconfdir}/%{name}/config.inc.php
rm -rf %{buildroot}/var/www/%{name}/conf

# generate UTF-8 files
pushd lang
    make DESTDIR=./recoded
popd
install -m0644 lang/recoded/*.php  %{buildroot}/var/www/%{name}/lang/recoded/

# cleanup
pushd %{buildroot}/var/www/%{name}
    rm -rf sql
    rm -f CREDITS DEVELOPERS FAQ HISTORY INSTALL LICENSE TODO TRANSLATORS
    rm -f lang/Makefile lang/convert.awk lang/php2po lang/po2php lang/synch lang/langcheck
popd

cat > %{buildroot}%{webappconfdir}/%{name}.conf << EOF
Alias /%{name} /var/www/%{name}

<Directory /var/www/%{name}>
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{webappconfdir}/%{name}.conf"
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
Comment=phpPgAdmin is a web administration GUI for PostgreSQL.
Exec=%{_bindir}/www-browser http://localhost/%{name}/
Icon=%{name}
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Databases;
EOF

%post
ccp --delete --ifexists --set "NoOrphans" --ignoreopt config_version \
    --oldfile %{_sysconfdir}/%{name}/config.inc.php \
    --newfile %{_sysconfdir}/%{name}/config.inc.php.rpmnew
%if %mdkversion < 201010
%_post_webapp
%endif
%if %mdkversion < 200900
%update_menus
%endif

%postun
%if %mdkversion < 201010
%_postun_webapp
%endif
%if %mdkversion < 200900
%clean_menus
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CREDITS DEVELOPERS FAQ HISTORY INSTALL LICENSE TODO TRANSLATORS sql/reports-pgsql.sql
%config(noreplace) %{webappconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%attr(0640,apache,root) %config(noreplace) %{_sysconfdir}/%{name}/config.inc.php
/var/www/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop
