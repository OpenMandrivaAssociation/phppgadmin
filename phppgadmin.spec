%define rname phpPgAdmin

Summary:        Intended to handle the adminstration of PostgreSQL over the web
Name:           phppgadmin
Version:        4.2.2
Release:        %mkrel 1
License:        GPL
Group:          System/Servers
URL:            http://sourceforge.net/projects/phppgadmin
Source0:        http://prdownloads.sourceforge.net/phppgadmin/%{rname}-%{version}.tar.bz2
Patch0:         phpPgAdmin-4.1.1-mdv_conf.diff
Requires(pre):  apache-mod_php
Requires(pre):  php-pgsql
Requires(pre):  php-gettext
Requires(post): ccp >= 0.4.0
Requires(post): rpm-helper
Requires(postun): rpm-helper
BuildRequires:  apache-base >= 2.0.54
BuildRequires:  file
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

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

export DONT_RELINK=1

install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
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

cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf << EOF

Alias /%{name} /var/www/%{name}

<Directory /var/www/%{name}>
    Allow from All
</Directory>

# Uncomment the following lines to force a redirect to a working
# SSL aware apache server. This serves as an example.
#
#<IfModule mod_ssl.c>
#    <LocationMatch /%{name}>
#        Options FollowSymLinks
#        RewriteEngine on
#        RewriteCond %{SERVER_PORT} !^443$
#        RewriteRule ^.*$ https://%{SERVER_NAME}%{REQUEST_URI} [L,R]
#    </LocationMatch>
#</IfModule>

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
ccp --delete --ifexists --set "NoOrphans" --ignoreopt config_version --oldfile %{_sysconfdir}/%{name}/config.inc.php --newfile %{_sysconfdir}/%{name}/config.inc.php.rpmnew
%_post_webapp
%if %mdkversion < 200900
%update_menus
%endif

%postun
%_postun_webapp
%if %mdkversion < 200900
%clean_menus
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CREDITS DEVELOPERS FAQ HISTORY INSTALL LICENSE TODO TRANSLATORS sql/reports-pgsql.sql
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%dir %attr(0755,root,root) %{_sysconfdir}/%{name}
%attr(0640,apache,root) %config(noreplace) %{_sysconfdir}/%{name}/config.inc.php
/var/www/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop
