%define rname phpPgAdmin

Summary:	PostgreSQL database adminstration over the web interface
Name:		phppgadmin
Version:	4.2.3
Release:	5
License:	GPLv2+
Group:		System/Servers
URL:		http://sourceforge.net/projects/phppgadmin
Source0:	http://prdownloads.sourceforge.net/phppgadmin/%{rname}-%{version}.tar.bz2
Patch0:		phpPgAdmin-4.1.1-mdv_conf.diff
Requires:	apache-mod_php
Requires:	php-pgsql
Requires:	php-gettext
Requires(post): ccp >= 0.4.0

%if %mdkversion < 201010
Requires(post):	rpm-helper
Requires(postun):   rpm-helper
%endif

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
	make DESTDIR=./recoded
popd
install -m0644 lang/recoded/*.php  %{buildroot}/var/www/%{name}/lang/recoded/

# cleanup
pushd %{buildroot}/var/www/%{name}
	rm -rf sql
	rm -f CREDITS DEVELOPERS FAQ HISTORY INSTALL LICENSE TODO TRANSLATORS
	rm -f lang/Makefile lang/convert.awk lang/php2po lang/po2php lang/synch lang/langcheck
popd

cat > %{buildroot}%{_webappconfdir}/%{name}.conf << EOF
Alias /%{name} /var/www/%{name}

<Directory /var/www/%{name}>
	Require host localhost.localdomain
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

%files
%doc CREDITS DEVELOPERS FAQ HISTORY INSTALL LICENSE TODO TRANSLATORS sql/reports-pgsql.sql
%config(noreplace) %{_webappconfdir}/%{name}.conf
%dir %{_sysconfdir}/%{name}
%attr(0640,apache,root) %config(noreplace) %{_sysconfdir}/%{name}/config.inc.php
/var/www/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop


%changelog
* Sat Aug 14 2010 Tomas Kindl <supp@mandriva.org> 4.2.3-1mdv2011.0
+ Revision: 569818
- bump to 4.2.3
- rephrased package summary, minor SPEC cleaning

* Sun Feb 07 2010 Guillaume Rousse <guillomovitch@mandriva.org> 4.2.2-4mdv2010.1
+ Revision: 501778
- switch default access policy to 'open to localhost only', as it allows to modify server state

* Sun Feb 07 2010 Guillaume Rousse <guillomovitch@mandriva.org> 4.2.2-2mdv2010.1
+ Revision: 501757
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Tue Dec 01 2009 Funda Wang <fwang@mandriva.org> 4.2.2-1mdv2010.1
+ Revision: 472168
- new version 4.2.2

* Tue Sep 15 2009 Thierry Vignaud <tv@mandriva.org> 4.2.1-3mdv2010.0
+ Revision: 441774
- rebuild

* Mon Dec 29 2008 Jérôme Soyer <saispo@mandriva.org> 4.2.1-2mdv2009.1
+ Revision: 320793
- Remove postgresql Requires Fix Bug #32700

* Mon Aug 18 2008 Funda Wang <fwang@mandriva.org> 4.2.1-1mdv2009.0
+ Revision: 273420
- update to new version 4.2.1

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 4.2-2mdv2009.0
+ Revision: 268964
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Wed Apr 16 2008 Funda Wang <fwang@mandriva.org> 4.2-1mdv2009.0
+ Revision: 194534
- update to new version 4.2

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 4.1.3-3mdv2008.1
+ Revision: 171042
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Thu Oct 11 2007 Oden Eriksson <oeriksson@mandriva.com> 4.1.3-2mdv2008.1
+ Revision: 97002
- drop the quotes in the Exec= line (blino)

* Sat Sep 01 2007 Funda Wang <fwang@mandriva.org> 4.1.3-1mdv2008.0
+ Revision: 77356
- New version 4.1.3

* Tue Jun 05 2007 David Walluck <walluck@mandriva.org> 4.1.2-1mdv2008.0
+ Revision: 35259
- 4.1.2
- Requires(post,postun): rpm-helper

* Fri May 11 2007 Jérôme Soyer <saispo@mandriva.org> 4.1.1-1mdv2008.0
+ Revision: 26311
- Ajout d'un BuildRequires
- New release 4.1.1


* Tue Mar 27 2007 Oden Eriksson <oeriksson@mandriva.com> 4.0.1-5mdv2007.1
+ Revision: 148969
- fix patch to the config file in the patch
- use the common www-browser script

  + Jérôme Soyer <saispo@mandriva.org>
    - Lowercase

* Sun Feb 18 2007 Nicolas Lécureuil <neoclust@mandriva.org> 4.0.1-4mdv2007.1
+ Revision: 122575
- Fix typo found by berthy
- Import phpPgAdmin

