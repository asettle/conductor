%global app_root %{_datadir}/%{name}
%global doc_root %{_datadir}/%{name}-doc

Name:     aeolus-conductor
Version:  0.8.16
Release:  1%{?dist}
Summary:  The Aeolus Conductor

Group:    Applications/System
License:  ASL 2.0 and MIT and BSD
URL:      http://aeolusproject.org

# to build source tarball
# git clone  git://git.fedorahosted.org/aeolus/conductor.git
# git checkout v0.3.0_RC_1
# make dist
# cp aeolus-conductor-0.3.0.tar.gz ~/rpmbuild/SOURCES
Source0:    aeolus-conductor-%{version}.tar.gz

Requires: system-logos
Requires: ruby >= 1.8.1
Requires: ruby(abi) = 1.8
Requires: rubygem(rails) >= 3.0.7
Requires: rubygem(haml) >= 3.1
Requires: rubygem(nokogiri) >= 1.4.0
Requires: rubygem(will_paginate) >= 3.0
Requires: rubygem(deltacloud-client) >= 0.4.0
Requires: rubygem(simple-navigation)
Requires: rubygem(rest-client) >= 1.6.1
Requires: rubygem(builder)
Requires: rubygem(json)
Requires: rubygem(rack-restful_submit)
Requires: rubygem(uuidtools)
Requires: rubygem(fastercsv)
Requires: rubygem(rails_warden)
Requires: rubygem(aeolus-image) >= 0.1.0-4
Requires: rubygem(pg)
Requires: rubygem(ruby-net-ldap)
Requires: rubygem(oauth)
Requires: rubygem(rake)
Requires: postgresql
Requires: postgresql-server
Requires: system-logos

# to ensure the service is actually started
# and is accessible in the init script
Requires: curl

BuildRequires: rubygem(sass)

BuildArch: noarch

%description
The Aeolus Conductor, a web UI for managing cloud instances.

%package daemons
Summary:   Aeolus Conductor daemons
Group:     Applications/Internet
License:   ASL 2.0
Requires: %{name} = %{version}-%{release}
Requires: httpd >= 2.0
Requires: rubygem(thin) >= 1.2.5
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts

%description daemons
The configuration and daemons necessary to run and proxy the Aeolus Conductor.

%package doc
Summary: Aeolus Conductor documentation
Group:   Documentation
Requires: %{name} = %{version}-%{release}

%description doc
Documentation for the Aeolus Conductor.

%package devel
Summary: Aeolus Conductor development and testing files
Group:   Applications/Internet
Requires: %{name} = %{version}-%{release}
Requires: rubygem(cucumber)
Requires: rubygem(rspec)
Requires: rubygem(timecop)
Requires: rubygem(cucumber-rails)
Requires: rubygem(rspec-rails) >= 2.6.1
Requires: rubygem(capybara) >= 1.0.0
Requires: rubygem(database_cleaner) >= 0.5.0
Requires: rubygem(factory_girl)
Requires: rubygem(vcr)
Requires: rubygem(factory_girl_rails)
Requires: rubygem(webmock)
Requires: rubygem(launchy)

%description devel
Tests and other development tools for the Aeolus Conductor.

%package -n aeolus-all
Summary:  A meta-package to pull in all components for Aeolus
Group:    Applications/Internet
Requires: aeolus-conductor-daemons = %{version}-%{release}
Requires: aeolus-conductor-doc = %{version}-%{release}
Requires: iwhd
Requires: aeolus-configure
Requires: imagefactory
Requires: imagefactory-jeosconf-ec2-fedora
Requires: imagefactory-jeosconf-ec2-rhel
Requires: rubygem(aeolus-image)
Requires: rubygem(aeolus-cli)
Requires: mongodb-server
Requires: mod_ssl
Requires: deltacloud-core
Requires: deltacloud-core-ec2
Requires: deltacloud-core-rhevm
Requires: deltacloud-core-vsphere
Requires: ntp
Requires: rsyslog-relp

%description -n aeolus-all
This is the aeolus meta-package.  If you want to install aeolus and all of its
dependencies on a single machine, you should install this package and then
run aeolus-configure to configure everything.

%prep
%setup -q

%build

%pre
getent group aeolus >/dev/null || /usr/sbin/groupadd -g 180 -r aeolus 2>/dev/null || :
getent passwd aeolus >/dev/null || \
    /usr/sbin/useradd -u 180 -g aeolus -c "aeolus" \
    -s /sbin/nologin -r -d /var/aeolus aeolus 2> /dev/null || :

%install
%{__mkdir} -p %{buildroot}
%{__mkdir} -p %{buildroot}%{app_root}
%{__mkdir} -p %{buildroot}%{doc_root}
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__mkdir} -p %{buildroot}%{_sysconfdir}/httpd/conf.d
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d

%{__mkdir} -p %{buildroot}%{_localstatedir}/lib/%{name}
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir} -p %{buildroot}%{_localstatedir}/run/%{name}
%{__mkdir} -p %{buildroot}/%{_bindir}

# now copy over the rails source files.  This is a bit verbose, but only
# takes in the stuff we need (and no backup files, etc)

# we use these special constructs to find only the files we care about.
# the name of the variable has to be the file extension you are looking for.
# the contents of the variable are the directories in which files with this
# extension may exist.  For instance cgi="public" means that src/public/*.cgi
# will be copied from the source into the RPM.
builder="app/views/errors"
css="public/stylesheets public/stylesheets/jquery.ui-1.8.1 \
     public/javascripts/jquery-svg"
feature="features"
gif="public/images public/stylesheets/images"
haml="app/views/hardware_profiles app/views/realm_mappings \
      app/views/users app/views/provider_accounts \
      app/views/roles app/views/providers app/views/settings \
      app/views/realms app/views/pool_families app/views/layouts\
      app/views/quotas app/views/permissions \
      app/views/deployments app/views/pools \
      app/views/instances app/views/user_sessions \
      app/views/deployables app/views/catalogs \
      app/views/provider_types app/views/api/images \
      app/views/config_servers app/views/provider_realms \
      app/views/api/hooks \
      app/views/api \
      app/views/images \
      app/views/api/builds app/views/api/provider_images \
      app/views/api/target_images app/views/api/entrypoint \
      app/views/api/environments"
html="public"
ico="public"
jpg="public/images public/stylesheets/images"
js="public/javascripts public/javascripts/jquery-svg \
    public/javascripts/jquery.ui-1.8.1 \
    public/javascripts/jquery.ui-1.8.1/ui/minified \
    public/javascripts/backbone"
json="spec/fixtures"
key="features/upload_files"
opts="spec"
png="public/images public/images/icons public/stylesheets/images \
     public/stylesheets/jquery.ui-1.8.1/images"
rake="lib/tasks"
rb="app/models app/controllers app/controllers/api app/helpers app/services app/util \
    config config/initializers config/environments db db/migrate \
    features/support features/step_definitions lib spec spec/controllers \
    spec/factories spec/helpers spec/models spec/services spec/controllers/api lib/aeolus \
    lib/aeolus/event"
rhtml="app/views/layouts"
svg="public/images public/images/icons public/javascripts/jquery-svg"
ttf="public/fonts"
txt="public"
yml="config config/locales config/locales/defaults config/locales/overrides \
     config/locales/role_definitions config/locales/activerecord \
     config/locales/overrides/role_definitions config/locales/overrides/activerecord"
xml="app/util"
for filetype in builder css feature gif haml html ico jpg js json key opts png \
    rake rb rhtml scss svg ttf txt yml xml; do
    dirs=${!filetype}

    for dir in $dirs; do
        %{__mkdir} -p %{buildroot}%{app_root}/$dir
	for i in $(echo src/$dir/*.$filetype); do
            test -e "$i" && %{__cp} "$i" %{buildroot}%{app_root}/$dir
        done
    done
done
%{__rm} %{buildroot}%{app_root}/config/initializers/secret_token.rb

# precompile stylesheets
%{__mkdir} %{buildroot}%{app_root}/public/stylesheets/compiled
sass --style compact ./src/app/stylesheets/custom.scss %{buildroot}%{app_root}/public/stylesheets/compiled/custom.css
sass --style compact ./src/app/stylesheets/layout.scss %{buildroot}%{app_root}/public/stylesheets/compiled/layout.css
sass --style compact ./src/app/stylesheets/login.scss %{buildroot}%{app_root}/public/stylesheets/compiled/login.css

# misc files
%{__cp} src/Rakefile %{buildroot}%{app_root}
%{__cp} src/config.ru %{buildroot}%{app_root}
%{__cp} src/lib/aeolus/debug/aeolus-debug %{buildroot}%{_bindir}

%{__mkdir} -p %{buildroot}%{app_root}/config
%{__cp} src/config/database.pg %{buildroot}%{app_root}/config
%{__cp} src/config/database.mysql %{buildroot}%{app_root}/config
%{__cp} src/config/database.sqlite %{buildroot}%{app_root}/config
# here we copy the postgres configuration to be the default.  While this is
# something of a policy we are encoding in the RPM, it is nice to give the user
# sane defaults.  The user can still override this with their own configuration
%{__cp} src/config/database.pg %{buildroot}%{app_root}/config/database.yml

%{__mkdir} -p %{buildroot}%{app_root}/dbomatic
%{__cp} src/dbomatic/dbomatic %{buildroot}%{app_root}/dbomatic

# move documentation to the correct place
%{__cp} src/doc/* %{buildroot}/%{doc_root}

# copy over init scripts and various config
%{__cp} conf/aeolus-conductor %{buildroot}%{_initrddir}
%{__cp} conf/conductor-dbomatic %{buildroot}%{_initrddir}
%{__cp} conf/aeolus-conductor-httpd.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/aeolus-conductor.conf
%{__cp} conf/aeolus-conductor.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/aeolus-conductor
%{__cp} conf/aeolus-conductor.sysconf %{buildroot}%{_sysconfdir}/sysconfig/aeolus-conductor
%{__cp} conf/conductor-rails.sysconf %{buildroot}%{_sysconfdir}/sysconfig/conductor-rails
%{__mkdir} -p %{buildroot}%{_libdir}/../lib/tmpfiles.d
%{__cp} conf/aeolus-tmpfiles.conf %{buildroot}%{_libdir}/../lib/tmpfiles.d/aeolus.conf

%{__mkdir} -p %{buildroot}%{app_root}/config/image_descriptor_xmls

# Creating these files now to make sure the logfiles will be owned
# by aeolus:aeolus. This is a temporary workaround while we've still
# got root-owned daemon processes. Once we resolve that issue
# these files will no longer be added explicitly here.
touch %{buildroot}%{_localstatedir}/log/%{name}/thin.log
touch %{buildroot}%{_localstatedir}/log/%{name}/rails.log
touch %{buildroot}%{_localstatedir}/log/%{name}/dbomatic.log

%{__mkdir} -p %{buildroot}%{app_root}/log

# copy script files over
%{__cp} -r src/script %{buildroot}%{app_root}

# link the redhat logo
ln -svf %{_sysconfdir}/favicon.png %{buildroot}%{app_root}/public/images/favicon.png

%{__mkdir} -p %{buildroot}%{_sysconfdir}/%{name}

%post
# symlink the configuration bits from /usr/share/aeolus-conductor/config
# into /etc/aeolus-conductor.  Note that we unceremoniously use -f here;
# if the user had broken the symlinks and put data in here, it would have been
# completely ignored *anyway*
# Generate OAuth configuration:
pushd %{app_root} 2>&1 > /dev/null
export RAILS_ENV=production; rake dc:oauth_keys 2>&1 > /dev/null
popd 2>&1 > /dev/null

%{__ln_s} -f %{app_root}/config/environments/development.rb %{_sysconfdir}/%{name}
%{__ln_s} -f %{app_root}/config/environments/production.rb %{_sysconfdir}/%{name}
%{__ln_s} -f %{app_root}/config/environments/test.rb %{_sysconfdir}/%{name}
%{__ln_s} -f %{app_root}/config/database.yml %{_sysconfdir}/%{name}
%{__ln_s} -f %{app_root}/config/settings.yml %{_sysconfdir}/%{name}
%{__ln_s} -f %{app_root}/config/oauth.json %{_sysconfdir}/%{name}

%postun
# kind of a weird construct.  There are two cases where postun gets called;
# during the removal of a package and during the cleanup after an upgrade.
# During removal, we want to remove the symlinks; during upgrade we do not.
# Therefore, we check to see if app_root/app is still there; if it is,
# then we assume it is an upgrade and do nothing, otherwise we assume it is
# a removal and delete the symlinks
if [ ! -d %{app_root}/app ]; then
   rm -f %{_sysconfdir}/%{name}/development.rb
   rm -f %{_sysconfdir}/%{name}/production.rb
   rm -f %{_sysconfdir}/%{name}/test.rb
   rm -f %{_sysconfdir}/%{name}/database.yml
   rm -f %{_sysconfdir}/%{name}/settings.yml
fi

%post daemons
# Register the services
/sbin/chkconfig --add aeolus-conductor
/sbin/chkconfig --add conductor-dbomatic

%preun daemons
if [ $1 = 0 ]; then
   /sbin/service aeolus-conductor stop > /dev/null 2>&1
   /sbin/chkconfig --del aeolus-conductor
   /sbin/service conductor-dbomatic stop > /dev/null 2>&1
   /sbin/chkconfig --del conductor-dbomatic
fi

%files
%dir %{app_root}
%{app_root}/app
%defattr(640,root,aeolus,750)
%dir %{app_root}/config
%{app_root}/config/environments
%{app_root}/config/initializers
%{app_root}/config/locales
%{app_root}/config/*.rb
%{app_root}/config/database.mysql
%{app_root}/config/database.pg
%{app_root}/config/database.sqlite
%config %{app_root}/config/*.yml
%defattr(-,root,root,-)
%{app_root}/config.ru
%{app_root}/db
%{app_root}/dbomatic
%{app_root}/lib
%{_bindir}/aeolus-debug
%{app_root}/log
%{app_root}/public
%{app_root}/Rakefile
%config %{_sysconfdir}/%{name}
%doc AUTHORS COPYING

%files daemons
%{_initrddir}/aeolus-conductor
%{_initrddir}/conductor-dbomatic
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/aeolus-conductor
%config(noreplace) %{_sysconfdir}/sysconfig/conductor-rails
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%attr(-, aeolus, aeolus) %{_localstatedir}/lib/%{name}
%attr(-, aeolus, aeolus) %{_localstatedir}/run/%{name}
%attr(-, aeolus, aeolus) %{_localstatedir}/log/%{name}
%doc AUTHORS COPYING
%{_libdir}/../lib/tmpfiles.d/aeolus.conf

%files doc
%{doc_root}
%doc AUTHORS COPYING

%files devel
%{app_root}/features
%{app_root}/script
%{app_root}/spec

%files -n aeolus-all

%changelog
* Wed May 23 2012 Tzu-Mainn Chen <tzumainn@redhat.com> 0.8.16-1
- 

* Wed May 23 2012 Tzu-Mainn Chen <tzumainn@redhat.com> 0.8.15-1
- 878aeec BZ806001 - aeolus-configure will always create an admin user, need to
  key of a uuid not name

* Thu May  3 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.14-1
- Build with tito

* Fri Apr 20 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.13-1
- 5cda012 Revert "BZ 796528 - deployment launch refactoring"
- d096251 Revert "BZ 796528 - instance's config params are now handled from taskomatic"
- 72e9d7d Revert "BZ 796528 - set CREATE_FAILED status for instances which failed to launch"
- fb49957 Revert "BZ 796528 - updated tests"

* Wed Apr 18 2012 Steve Linabery <slinaber@redhat.com> - 0.8.12-1
- e451adc BZ #813924 - Clean up JavaScript handling of form change events

* Wed Apr 18 2012 Steve Linabery <slinaber@redhat.com> - 0.8.11-1
- 635ccf3 BZ 800849 - CREATE_FAILED instances will not be marked as vanished

* Mon Apr 16 2012 Steve Linabery <slinaber@redhat.com> - 0.8.10-1
- d7f461b BZ 796528 - updated tests
- a0659d9 BZ 796528 - set CREATE_FAILED status for instances which failed to launch
- 1542028 BZ 796528 - instance's config params are now handled from taskomatic
- 08a0394 BZ 796528 - deployment launch refactoring
- 4799400 BZ 786207 - selection validation on launch_new
- 23de72c BZ 803647 - Persist pool[pool_family_id] on failure during creation

* Thu Apr 12 2012 Steve Linabery <slinaber@redhat.com> - 0.8.9-1
- 141d399 BZ #810404: Some GPL files that should be ASL
- 91b76e4 BZ 809710 fixed name of interpolated argument for images.new.description

* Thu Apr 12 2012 Steve Linabery <slinaber@redhat.com> - 0.8.8-1
- 4244f63 BZ#795902 Provide Unique Names for Cloud Resource Cluster

* Thu Mar 29 2012 Steve Linabery <slinaber@redhat.com> - 0.8.7-1
- 64bd4e1 BZ 803948 Fix of filters options in filter tables
- 876f609 Reverting changes of BZ 803948 bugfix in models
- a393e0e Reverting changes of BZ 803948 bugfix in views

* Wed Mar 28 2012 Steve Linabery <slinaber@redhat.com> - 0.8.6-1
- 4cc32b8 BZ807436: Fix login error message on IE8
- 9da9169 BZ807462: Fix filter view detection
- b65daa9 BZ 803948 Fix of filters options in filter tables
- da239a4 BZ 803948 Fix of filters options in filter tables
- b4f044b BZ 804620 added i18n for some fields in form of pools rev.
- aa574bd BZ 804620 added i18n for some fields in form of pool families
- 4c97201 BZ 804620 Added i18n for some fields in form of deployables

* Wed Mar 28 2012 Steve Linabery <slinaber@redhat.com> - 0.8.5-1
- 9b1de4b BZ807727 aeolus-conductor should not depend on rubygem(sqlite3)
- f8bf08b BZ 807342 added src/config/locales/defaults

* Tue Mar 27 2012 Steve Linabery <slinaber@redhat.com> - 0.8.4-1
- b2ab194 BZ #805586 - HWP match preview fix
- c79a5cd BZ #805586 - HWP match preview fix
- cc4e941 Added Japanese activerecord dictionary
- 6989372 Added Japanese overrides/activerecord dictionary
- 2a9bd91 Added Japanese dictionary
- 8c6a0c5 Added overrides Japanese dictionary
- 0bd4d20 Added Japanese role_definitions dictionary
- f1bba56 Added Japanese overrides/role_definitions dictionary
- 7411f66 Added French overrides/role_definitions dictionary
- 9b1f676 Added French role_definitions dictionary
- 2652d89 Added overrides French dictionary
- faa6633 Added French dictionary
- 332680d Added overrides/activerecord French dictionary
- 26f8f7b Added activerecord French dictionary
- dcd63d5 BZ 802830 remove remaining overrides that mistakenly turn 'images' into 'component outlines'
- 98f96cd BZ 803628 remove non-existent classnames locales; replace them with activerecord locales

* Tue Mar 20 2012 Steve Linabery <slinaber@redhat.com> - 0.8.3-1
- 7cfbd07 BZ 803249 - Remove qpidd as dependency
- 404d5c1 BZ 802847 - fix hwp matching when there are multiple values for architecture

* Mon Mar 19 2012 Steve Linabery <slinaber@redhat.com> - 0.8.2-1
- d637efc BZ 798549 added additional rescue cases when trying to import xml from url
- 61ff2ec bug 802869: Add system-logos dep for favicon.png
- 6d239a6 BZ 803586 fix provider_realms override
- 9c3dd9f BZ795239 Typo in en.yml locale file

* Fri Mar 16 2012 Steve Linabery <slinaber@redhat.com> - 0.8.1-1
- f6fd3b4 BZ 801911 added checks before destroying a pool family
- aef0d90 BZ 801911 check that pools are destroyable before destroying a pool family
- ff32272 BZ 801911 added/clarified text related to pool family deletion
- 6ce6d44 bug 801193: permissions UI rendering error with 'test account'
- 5f62666 Removes inapplicable test
- 8ac5874 Fixes failing test
- 3ab5bce BZ 802830 updated image tab tag for consistency
- f804225 BZ 802830 removed unnecessary overrides that mistakenly replaced 'image' with 'component outline'
- 7facfc3 BZ 801911 added/updated overrides dealing with cloud deletion

* Wed Mar 14 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-43
- 01c0e60 BZ 798549 removed humanize_error, added in 'require util/conductor'
- 22f2eb0 BZ 798549 added exception handling and humanize_error to catch connection refused errors
- db4c031 BZ 798549 added humanize_error
- 2d184a2 Bug 788465: Don't allow a Realm Admin to map to realms or providers without USE permission on the provider.
- 1ff3098 BZ800308 removed duplicate cancel button in catalog and pool forms
- 257faed bug 801106: limit pool selection within pool family for catalog edit
- 18ae4bc bug 790735: Enforce image permissions on deleting imported images https://bugzilla.redhat.com/show_bug.cgi?id=790735
- e8c1396 BZ801199: Change latest_build to the latest in time
- 6ff17f0 BZ802485 Update product name overrides
- 73ec93c BZ-795902-Provide Unique Names for Cloud Resource Cluster
- a63f8f6 BZ798575 and BZ798555 product changes
- 47774c1 BZ#798287 Fix the product name from Aeolus to Cloud Engine
- 588cc86 BZ796388 Fix product name on Launch Deployment page
- 80092df bug 800511: update overrides/en.yml for role changes
- f198670 bug 800511: update roles list and default user roles
- ff518fa BZ800308 removed duplicate cancel button in catalog and pool forms
- 64f73f3 BZ 800014 - removed fake czech localization
- f56f211 BZ798575 removed classnames translations and replaced it with activerecord translations
- ea4f3b6 BZ798575 added provider_realm mappings translations

* Mon Mar 12 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-42
- 2836626 BZ 801089 always allow user to click through to pool_family details
- ab5c536 BZ798555 added default translations from rails-i18n gem which should be used in later versions
- 8324256 BZ798555 added default translations from rails-i18n gem which should be used in later versions

* Tue Mar 06 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-41
- 87af1bf BZ 788136 add checks to see if accounts exist
- d591293 BZ 795666 show proper error if user does not have permission to destroy a pool
- 3d4d3eb Added rspec test for reaching of user's quota
- e1f832d BZ 799306 User quota not enforced for multi-instance deployment
- e2f71a3 BZ 798567 use Il8n version of unlimited
- d8f2de2 BZ 798567 fix to allow Il8n'd version of 'unlimited' to count as unlimited
- 70afaf5 BZ 798548 - fixed redirect on image import fail
- 17ede53 BZ798570 reworked more_actions dropdown to align properly
- 2b8186b BZ #791123 catch deltacloud exceptions in dbomatic
- ab6847b BZ 799270 perform character replacment in 'name' prior to uniqueness validation
- eb75c9d BZ #798080: aeolus-conductor RPM outputs to stdout
- 65b6216 BZ#799913 Removed wrong buttons from edit deployables page
- 2d774ea Enable ajax update via backbone on /deployables/:id
- 861a8fc BZ798026 Explicit none_selected messages to deployments and instances lists
- a2a8f2f BZ798026 Unified popup messages into one js method, enabled translation
- 9d1fa70 BZ798550 added clearfix to administer section form input wrapper elements, to prevent skipping to the side when label is long
- 388b602 Revert "BZ794536 Timeout session after 15 minutes of inactivity"
- b812463 Bug 788148: Moved catalog entry tests to deployables spec
- e6305cb bug 788148: some permissions checking fixes to enable proper 'environment admin' functionality
- 3cb14d5 bug 788148: Add permissions pane to provider accounts UI
- fcd2f30 bug 788148: seeds.rb update to update role definitions https://bugzilla.redhat.com/show_bug.cgi?id=788148
- c15f925 bug 788148: whitespace changes for readibility
- 58afc18 bug 788148: Take environment into account for permission inheritance
- 2926437 BZ 788558 - instance termination for single instance
- dea36d7 BZ-790026-Deleting a provider with running instances does not show any message
- ca45908 BZ 799314 - Override wrong_environment en.yml key
- ff99903 BZ 799314 - Clarify error when a deployable has images in the wrong environment.
- 74ff94a BZ 798136 - Fix reference to 'Environment'
- 6b9c697 BZ798574: Separating matching_provider_hardware_profiles action from create
- fac0ade BZ799492: Fix "push is about to start" message
- b2cc877 BZ797208: Enable push all button on autoupdate
- c9d5bf6 BZs #798501 and #798505: Product names should be pulled from mapping file
- 58a94ec BZs #798501 and #798505: Object names should be pulled from mapping file
- 2ace270 BZ796562 Fix environment i18n in image properties

* Fri Mar 02 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-40
- 9f329e2 BZ 795655 "Return to User" is not required to show for non-admin's
- 16ded28 BZ#790250 Check Build Status on Show Image - jQuery template
- 7ae60f4 BZ798570 Fixed filter table action buttons alignment, added more-actions dropdown tables where more than two action buttons occur
- 8406c70 BZ788048: Fix permission checking on pools/_images
- 79efbfa BZ 798515 - Render correct error message when deleting user
- fe54ef0 Do not offer to delete imported provider images
- 485d0b1 BZ 798347 added breadcrumb back to realms index
- 5cfa1b7 BZ 799050 - Initialize @details_tab outside of filter_view
- 528a874 BZ 796695 enforce provider quota for multi instance deployments
- 7b774b0 BZ 784479 add range validation to priority
- 2dfe3a6 BZ 798259 - require_user handles XHR requests properly
- 245f766 BZ790861, BZ788103 Remove only catalog entry when removing deployable from catalog detail page
- 1e77195 BZ796862 Launch Time Params, if parameter has new lines in its value, its put into textarea instead of text input
- dfc7155 BZ784474 added word-wrap: break-word to all headers, so long words dont get off the ui

* Wed Feb 29 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-39
- 361d50b BZ #796797: Move Role strings out of seeds.rb to allow overrides
- 369b094 bug 788148: Removing failing cucumber test for obsolete UI.
- eb85c8e BZ#795523 Updated tdl.rng to validate OS name
- ccb766c Updated tdl.rng to set rootpw element to optional
- 7967c5d BZ#790250 Check Build Status on Show Image
- bec9399 BZ 790860 - improved availability checking
- 774cad0 BZ #796797: Move Role strings out of seeds.rb to allow overrides.
- e3b5bb6 BZ-788547 Unhandled exception or status code , when launching with space in deployments name for RHEV
- 93ebda8 Fix typo in locales/en.yml
- 8f674f5 Architecture is displayed for imported images.
- 87bd40b BZ 796800 - Disallow Environment actions if Environment has no Pools
- 0305773 BZ 796052 - Fix language on image imports
- 61370d1 BZ 796052 - Image Import tab added to Environments page

* Tue Feb 28 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-38
- 00dc1dd BZ797713 added missing translation in edit deployable page
- 1d1a3fb BZ789853 added rescue connection timeout
- d9ca535 BZ#790819 Add better labels to X-Deltacloud-Provider field
- 30dde81 Fix broken Pools cucumber test
- a38a265 BZ794536 Timeout session after 15 minutes of inactivity
- 29fabcd BZ 790820 remove unsupported cloud provider types

* Mon Feb 27 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-37
- 5a587b0 BZ 797254 - Quick fix for failure to stop/reboot instances
- 7b1fc8e BZ 789833 strip login/username whitespace
- 6636b93 Fix Conductor.Views.PoolsIndex in case no deployment rendered
- 6e3a2a3 Adding persmission filter when displaying deployment
- 4419638 Added Japanese dictionary

* Thu Feb 23 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-36
- 40bb3e9 Bug 796783: fixes lingering errors w/ image import
- 00f79de BZ 790828 change 'upload' text to 'push'
- 11b5ebd Added French dictionary
- f36474d BZ 796805 - Merge aeolus-all into aeolus-conductor
- b1ac316 Removed config/database.yml.0 which was added accidentally

* Wed Feb 22 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-35
- 1296bf8 BZ 790820 remove unsupported cloud provider types
- 16e2b95 BZ#790434 Check unique assembly names on deployable xml
- 7b55f8c BZ 770716 added table.properties_table for Andy Fitzsimon
- 2379431 BZ #790434: Product name override
- 67da4c6 BZ796098 Fix UI inconsistencies
- 786c287 BZ #795794 - Don't delete :vanished instances
- 0e38628 BZ #795891 - Deployment should not show "running" with no instances
- 9a7e2a8 BZ #795794 - Display a saner error message if launch fails.
- d79165f BZ 788558 - allow terminate inaccessible instances on 'stop' action

* Wed Feb 22 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-34
- f02c06c Enable or disable launch button on deployables show page
- 3b907e5 BZ 790826 change rebuild_all text depending on context
- f7b2584 BZ 790826 added additional image build text
- 482675e BZ 791262 added no_results row if search returns no results
- 5239c6e BZ 791262 added search.no_results
- e6faaf5 Added check if there is provider account when adding provider account to poolfamily.
- b48b6c8 BZ790822 administer section form items alignment fix
- f48f4d1 BZ#795911 added cancel button to poolfamilies#new
- 34ab810 BZ790830: "Disable" upload button after it has been pressed on images#show (rebased)
- d87efb8 BZ#795921 Unsupported provider types are not listed in UI
- c6db2d0 BZ#790832 Don't filter out stopped instances from list view
- 5823613 BZ790831 Change and remove out of date text in deployable details page
- f650e46 BZ788612: fix merge conflict in layout.scss
- d20ded8 BZ790825: fix view inconsistencies between haml and jquery-template in images#show (rebased)
- ba7fc27 BZ-795909 Title bar on CloudForms Cloud Engine

* Tue Feb 21 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-33
- 25ddfb7 Add test for file exists before copy in aeolus-configure.spec.in
- bb1bb9c Decrease amount of time we keep rotated logs.
- 34c0ba2 BZ 791195 - Clean up destroy_on_provider code

* Tue Feb 21 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-32
- 8dbc82e BZ795691 Fix and unify return to links
- 9c591c2 BZ 790860 - re-enable provider availability
- 4958638 BZ#789363 Add appropriate Titles to the layout
- 3563b1a Fix minor syntax error.
- 406d02a BZ #795667: Build shows all old terms in UI
- 0982c10 https://bugzilla.redhat.com/show_bug.cgi?id=786010

* Mon Feb 20 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-31
- d86682c BZ 790824 hide build select unless build exists
- 61e2cd2 BZ 790516 - Only accept ipv4, hostname addresses for instances

* Mon Feb 20 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-30
- a3df89b BZ 781286 - Fix overlapping H1 with long image names
- 973cfb6 BZ 790827 added span.return_to css block
- b8e9d6b BZ 790827 wrap return_to section in span.return_to for easier formatting
- f405407 BZ #794759 - Pool Family page no longer runs thousands of SQL queries

* Mon Feb 20 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-29
- 9c9e210 BZ#788143 Fix missing translation on hwp deletion
- a1feb5e Added back button to Provider realm show view and localization
- 2ae1e9a BZ790833 Added confirmation to stopping deployment and stopping and restarting instances
- fae353b Don't check localised messages in deployment test
- 7fa7068 BZ788612: ui: make green New Image only
- db57195 BZ788612: ui: make green New Image only
- 3be52d6 BZ795350 Fix Pool Families table overlap
- 4420870 Internationalized breadcrumb controllers' names.
- 9ecfaae Move product i18n configuration to an override file
- eb69ab9 BZ 785196 fixed favicon link
- 31f1ae0 Add support for overriding default i18n file(s)
- f52be3c BZ 790620 added p.provider to allow for css-specific text formatting of provider name
- 6245e39 BZ 790620 changed stylesheet to decrease left margin in 'pretty boxes'; added p.provider to manage text overflow of provider name
- 6b80d72 Fix button_to form button styling when as single button in header
- edc6a44 BZ790901 Link to instance detail from deployment detail pretty view
- a3d2dcb BZ 790823 fix cancel redirect
- f378dd9 BZ 790828 replaced 'Upload' with 'Push'
- d2904d0 BZ 790828 added 'Push' text
- 787ce3a bug 786220 - Scope images to Pool Family
- 5a6dfd3 BZ 788397 block backbone from trying to match images/:id if trying to render edit_xml, overview, new, or import
- 8fd9e40 Removing redundant debug line
- f7ec99a BZ790816 Instance details page - tabbed sections

* Wed Feb 15 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-28
- a4ed54b fixed "Udate" type
- 4a4fcd5 BZ 790548 add spacing if there are multiple target image uuids
- ef3b665 Fix of UUIDs labels
- 7a022c0 BZ 786844 - Fix logic flaw in destroy_on_provider
- edeb5b7 BZ 786844 - Reporting of deleted instances

* Tue Feb 14 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-27
- 1088eed BZ#788863 Removed Sort links on New HWP Page
- 97e871b BZ 788350 Rename pools to "Cloud Resource Zone" in breadcrumb
- e021a52 BZ 788153 - Remove "All Rights Reserved" text.

* Mon Feb 13 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-26
- e545be6 BZ788841: fixed failing test for References to Realms removed
- 0eec133 References to Realms removed.
- 881b076 Unify badges alignment through app
- 999e744 BZ787810: Display availability status of providers and realms
- d848455 BZ 785196 updated favicon link
- 359ec8b BZ#789102 Default to first catalog of deployable if catalog not set
- df050c7 Replaced string in backbone.js view
- c8b9807 BZ 773027 Added partial of image's UUIDs
- 8c56c18 BZ 789000 change PoolsIndex to always use Conductor.Models.Pools, allowing for more consistent queries
- 5d3f4b5 BZ 789000 fix index to render proper json depending on tab
- 843b810 BZ 782574 add error messages when unable to connect to provider account/iwhd
- cb11552 BZ 782574 added exception if unable to connect to provider_account
- 2d0ba35 BZ783923 Prevent redisplaying previous filters by backbone when the view is refreshed
- 2fa8baf BZ#773226 Error message while rebooting stopped instances
- 300049e BZ#743377 Show deployable status in the pretty view

* Thu Feb 09 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-25
- 2bbd6bb BZ773034, BZ781482: Fix jQuery template on images#show
- 8654859 BZ 785094 - fixed cookie overflow and session store

* Wed Feb  8 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-24
- 21bbfbf BZ 788117 - Don't set session[:return_to] in UserSessions#new
- 44486b5 BZ 788018 Destroy deployables when deleting its last catalog
- 7b6fbd8 BZ 773247 fix for empty message header
- 2408968 BZ 783378 - log reboot (and other) instance action
- 8088844 https://bugzilla.redhat.com/show_bug.cgi?id=786207
- 419cb5a Make 2 deployables specs i18n-compatible
- 3cc70ff BZ 785742 - @template variable name conflicts with simple-navigation plugin

* Tue Feb  7 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-23
- db4bad8 BZ 788114 - Un-protects populate_realms method
- dc270e0 Fixed non i18n string in catalogs#new/edit form.
- 18f00af BZ#785223 Limit export instances scope
- d574184 BZ 785198 - Do not show broken builds in list
- 06f49c0 BZ 785198 - Do not build images for disabled providers

* Tue Feb  7 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-22
- c5963cf Added rspec examples for flash[:error] in deployables#new
- 3f387e9 BZ 782503 Wrong flash message when user try to create a new deployable from built & pushed image without any hardware profile.
- 6abd910 Larger administer navigation hover background image to accomodate nav items with long names
- fc98c7a BZ #784971: Diagnostics Tooling
- d973cbb BZ#753880 Catch exceptions on DC valid credentials request
- d03def7 BZ#783218 added pessimistic database locking for quota to prevent updating with old values
- c64db92 BZ 717987 (3) - Fixed error message when realm mapping not found
- 27d4b1d BZ 717987 (2) - added realms refresh
- fd15193 BZ 717987 (1) - Added realms available flag
- dc9e671 Bug 785892 Allow build for selective targets
- 730fd06 BZ 783904 PA quota when updated to unlimited, text should be automatically set to Unlimited.
- e23bbe6 Fixed 2 keys/values for successful conversion YAML to PO file
- 98708c0 BZ 783510 clean up\add css to instance details page
- e144151 BZ 787046 - reduce number of iwhd operations in deployments/overview
- caa1089 BZ 783075 added deployable.description to collapsed details for full display
- 4a7ef23 BZ 783075 updated css for long description on deployments/launch_from_catalog
- c4d02a9 BZ 784557 - send build request only if there are some providers

* Mon Feb  6 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-21
- bf7a0f1 permit empty first / last names in create_admin rake task
- 523be1f BZ 787280 - Remove unused links from footer
- 5aba1bc BZ 786612: change "New component outline" to green
- 8a80b0f BZ 786225 - New Image workflow tweak
- 3b39e52 Fix a typo in images#show
- 8cef905 BZ 743677 - stop/terminate instances when disabling inaccessible provider
- f976660 BZ 784564 - some running instances were not stopped when deleting a deployment
- d31f56e BZ 784499 added check to ensure task exists before saving
- 86c1cbe BZ 786865: Add THIN_LOCKFILE for improved service shutdown and status
- fc27711 Whitespace cleanup
- a770e80 Fixed login redirect-to-original-destination issue (BZ 782242).
- 69841ba Fixed 2 keys/values for successful conversion YAML to PO file
- 3767f28 Make some more tests i18n-independent

* Fri Feb  3 2012 John Eckersberg <jeckersb@redhat.com> - 0.8.0-20
- 3a5aa30 BZ786262 Fix missing navigation for Provider Realms
- 78cbf85 BZ 786344 added pre-launch validation for multi-instance deployments
- 3413bf7 BZ781579: Autoupdate for deployables#show
- 70a31de BZ 786581: ui: "Clouds" icon in /pool_families is now cloud
- 54fce80 BZ 785184: branding: shadowman's background from blue to red
- 1ee0024 BZ750957 Redirect to pools pretty view after creating pools
- 9ef3edb BZ 782879 fixes images count in images table in deployable detail page
- f143e2f BZ 785184: branding: shadowman's background from blue to red
- 559f99e BZ#782768 Fix a few typos in the Flash messages
- d109293 Fix the Launch button on Deployable Details page

* Thu Feb 02 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-19
- a50be41 BZ#785189 Removed sort urls from hwp table headers
- 64e9948 BZ#786126 Do not mass assign on credentials hash

* Thu Feb 02 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-18
- f99dfdb BZ 785196 added favicon.ico
- 55b3562 BZ785006 Clicking pool and deployment links in list view, leads to appropriate list view
- 3d9d3f6 BZ#785188 Remove the Aeolus logo from the footer
- 63d02c9 BZ#781604 Fix inconsistent Search behaviour on Enter keypress
- 87b172a BZ786452 Correct inconsistency in returning errors at API controllers
- d64aff3 BZ 785216 - Fix priority comparison for provider accounts
- 777517d BZ 785231: deployments: css for reworked launch time params form
- b2e101e BZ 785231: deployments: reworked launch time params form
- 74714ba Make 'rake spec' output more readable.
- 6a62246 Fix translation conflict in the footer
- e5f5e40 BZ 786162 removed help button from login page
- a4258fc BZ 783910 added missing priority information
- 9209d58 Fixing translation missing for to_sentence method
- 80bdb30 Fixing syntax error in model.js
- 2ed8e5b BZ 782336 ActiveRecord object is displayed in the failed instance column for pools.
- e2315c5 BZ773034: Autoupdate for images#show (rev. 3)
- 69c91b9 BZ 750504 Editing/Deleting backend Hardware Profiles
- 6d81de3 IE: Fix the missing images in the Administer navigation
- 26ed80c IE: Add the border to the User details card

* Tue Jan 31 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-17
- a1c5d20 Fixed flash[:notice] message in images#multi_destroy
- 4fcf20e BZ782788: remove permission based filtering of provider accounts on deployables#show
- dbbdb72 bug 784108: a bunch of permission tweaks to hide things from non-admins

* Mon Jan 30 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-16
- 1586711 BZ770377 - Better formatting for deployable exceptions
- d719d9e BZ770377 - Corrects realm mapping error text
- 0c49fc2 Remove console gem dep from lock file.
- f266327 provider realms search fix BZ770087
- 6f4ae15 BZ781482: feedback for image build/push failures

* Mon Jan 30 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-15
- 079be24 BZ 773247 fix to prevent empty flash header from popping up
- 9896920 BZ 785334 - fixed migration problem
- 23e9e78 Move the text in the footer to our I18n dictionary
- 2af0f68 catalog dropdown visibility fix

* Fri Jan 27 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-14
- dc5a853 Make tests (and app) work on mysql.
- 62184b2 BZ 773027 Add image,build,targetImage hash to deployable details
- c678fab BZ 781639: added column with Image UUID to provider images view
- d95ea37 Bug 772644: Add provider_account association to provider realm (revised)

* Thu Jan 26 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-13
- 0354906 Rebrands to finalized branding.
- 3c488a1 BZ 784183 - fixed provider name for deployments in mixed state
- 1dc9f2f BZ72277 image ready button in deplyable detail fix
- 345ad8e BZ#772353 Delete Imported Image when deleting imported target/provider image
- 2a92339 Update to the Cloud Forms terminology
- 92af3ee Update role names for 1.0 terminology
- 47827a3 BZ770087 fixes search functionality in provider's realm tab
- 6cb7044 BZ 783126 (part 2) - added 'push all' button to image show page
- 9366ff0 BZ 783126 (part 1) - Removed ProviderAccount.wrehouse_id method
- e43afe0 BZ 770358 - fixed image_status check
- 6f815ce BZ 783133 - removed build/push actions from deployable show page
- 5e9c09b Fixing pretty view toggle in pools#index
- 2470a0a BZ781353: Fix images#show in FF 3.6
- d4ad58b BZ770622: Filter for provider_type name on the list of deployments

* Wed Jan 25 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-12
- 53a5382 BZ 773261 added catalog parameter to catalog_entries.flash.notice.added
- 8e99c73 BZ 773261 updated catalog/deployable interaction messages to be clearer
- d60e281 BZ 783168 added whitespace trim to config_server parameters
- 743a4db BZ 744284 remove summary message when a deployment fails to launch
- 3ecb7b5 BZ 767759 - Launch multiple unique images
- ae989f6 bz781474 - add a default catalog
- c044de2 BZ767210 - "Users and Groups" tab now reads "Users"
- 8e3f29a BZ781286 - Set max-width on admin-page-header h1
- 71d0e6f User card shadow fix
- 8f4eafb Pool actions alignment fix
- be700a2 IE: fix the Instances pretty-view cards
- 5df589e Remove orphaned dictionary entries
- 5204f63 Make tests more I18n-friendly
- 8bcb085 Correct displaying of assemblies
- ffc5261 BZ772755, BZ773010, BZ773198: Change uptime label in deployment card

* Tue Jan 24 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-11
- e39090a Fixed deployable's tests after bugfix
- 17ed5c2 BZ 781257 Add flash message when deployable were deleted
- c76361b Pool families (Environments) table IE fix
- 1f47b6e BZ 773402 fixed deployment name test to limit length to 50
- 7990511 BZ#770911 Added N/A to missing fields on image list
- e1af83b Fix the key of flash error message in images_controller #show and in the dictionary file
- 21bef1c BZ#770354 added tests for priority field validation
- 7aab614 BZ#770354 added validation for priority field
- 49a0120 Added new tests after bugfix of BZ 743395 and reformat deployment_spec.rb for better reading
- dba3a9e BZ 743395 Fixed counting uptime
- fcfa0fa Fix the Add New Deployable form
- ae4908a IE: fix the broken layout for flash messages
- 7a1a020 BZ 783079 - fixed instance's destroy_on_provider
- ad1b2c3 BZ 783519 - replaced ActionError with general Exception
- 982a456 BZ 783096 - fixed error message for a provider deletion
- a11d6d6 Fixed (random) rspec test failure
- 97856dc user show page layout fixes (incl. IE)
- ace6e14 user dropdown styling and IE fixes (bz772784)
- c208e29 BZ 773402 enforce maximum length of 50 chars for names, as longer lengths result in creation errors
- 0e63199 BZ 783050 added description length validation
- 73ef4d5 BZ 773028 changed form to have more consistent layout with other admin forms
- e1375f0 BZ 782550 added check to see if there are associated providers
- bf2ce76 BZ 782550 add error message for images when no providers are enable
- 09f0997 BZ 783082 added warning message when deleting default pool

* Mon Jan 23 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-10
- d9d184f fixed EI login input text misalignment
- d89ced4 filter form elements IE fix
- dbccebc Provider selection and administer nav IE fixes. (bz740810, bz767844)
- 77b8787 IE: layout fix for Select deployable from catalog
- a9a0cb9 IE: fix the inconsistencies in the button heights
- 35abb05 IE: fix the catalog dropdown layout in pools#show
- c6bb710 BZ 773277 fixed logical operator mistake

* Fri Jan 20 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-9
- a75d3e3 BZ 782420 - Adds Image Administrator role
- 1f37ce5 IE: fix the Alerts layout in the Monitor section
- bb65570 IE fix for the New Pool button on pools#index
- 2fd73e2 IE: fix the pretty view cards spacing issue
- 7a89a23 Bug 767570: check deployable permissions on each step in the launch process
- 6175ea6 bug Bug 767563: Filter deployable list for user permissions
- 2d42777 fixes badges alignment
- b677082 Change version of gems in Gemfile.lock according to actual versions in F16
- 67a2d0d Fixing syntax error in application.js
- 67ec8b5 Fix pretty view toggle on deployments#show
- 881d8c2 Pretty view toggle restored on deployments#show
- 6d1364c Fix inline-block issue wchich caused errors in IE7
- 0c29b8c Fix our JavaScript code to load under IE
- ea1f3e8 Fix the horizontal lists under IE
- cab7259 Create a special IE 7 stylesheet
- b671774 BZ 754414 added summary statistics
- c87f1d6 BZ 754414 added pool_family.index.total_statistics
- 8c1c80c BZ 754414 added statistics method

* Wed Jan 18 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-8
- 98ded3f Merge branch '1.0-staging' into 1.0-product
- 6011cbf Replace casette bit dropped by fix for 745493
- d24dcbe BZ 772996: relabel "images ready", disable 'launch' before build
- ba48abf BZ770928: Change quota textfield when checking unlimited on pools#new
- ce855b6 BZ 767107 Fix spacing on the Create Deployable from Catalog page
- 36c73c4 BZ 773247 fixed flash error message type
- 7944078 Filter for provider name on the list of deployments
- 0a815f5 BZ 698665 - display ssh key pair name on instance show page
- aaabc4e BZ 771519 (part 3) - Added :url atribute to provider_account forms
- c092cb4 BZ 771519 (part 2) - HW profiles and realms population moved to create transaction
- e686cfb BZ 771519 (part 1) - Removed ProviderAccount observer
- 3d2f075 BZ 773466 - fixed exception handling of invalid template XML
- 7f0eb07 BZ 773466 - added cucumber test for this bug
- 942cd20 BZ 781450 - return 401 code for unauthenticated JSON requests
- 93b37dd BZ 767204 added pretty_view_toggle enabled to deployments tab
- 03a7783 BZ 767204 added data-pretty_view_toggle to tabs
- eeb9ddf Fixes failing test revealed by previous patch
- c3fb5c1 Adds description to Realms
- ade4d69 Blank default realm at launch now shows 'Auto-select'
- 1f32b4f BZ 752460 removed 'New Realm' button if viewing from provider
- 4ab0fc1 BZ771599: Restrict user deletion when user has running instances
- d95e5ee BZ 758644 - added rake task to decrement login counter
- 97dfda5 BZ 773074 fixed breadcrumb path in show method
- 8833ffd Bump release, add changelog 0.8.0-7

* Mon Jan 16 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-7
- 0d4bb59 Bump release, add changelog 0.8.0-6
- b124885 Merge branch '1.0-staging' into 1.0-product
- 1dcd95e Rebrand Aeolus as CloudForms Cloud Engine.
- 442a2ac Fix for https://bugzilla.redhat.com/show_bug.cgi?id=745493
- 1177784 BZ 773580 added redirect to account_url if user is not permissioned for admin
- 42fdc52 BZ 773580 changed html error message to display flash error
- 5030645 BZ 773580 replaced permission error message with locale message
- cea9245 BZ 773580 added permission_denied messages
- d72cfd2 Fixed rspec tests for bugfix in catalogs#destroy
- a3a023a BZ 770815 User shouldn't be able to delete a catalog, when its deployables have the last reference to this catalog.
- e0d3f8a Fixing deployment's json representation
- 74f4c22 BZ 770093 disabled actions for instances in STATE_PENDING
- 8e66f9d updated backbone templates to reflect alerts in deployments, pools and instances tables
- feb9518 Alerts in pools list, pool detail, deployment detail, alerts in pools list, deployments list, instances list tables
- e55da85 Show loadmask when switching pretty/filter views
- a5a9870 Fixing instance's json representation
- f032a28 Fixes message for deployment creation when no catalog selected
- 60089fd added cancel button
- 938f84d Removing redundant error messages from deployables#create
- 3e702e8 Change label if no catalog found
- f1640a0 Fixes box-sizing css issue appearing in chrome when included in table-like displayed div
- f9c98db More user friendly certs status in provider accounts form

* Fri Jan 13 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-6
- 1dcd95e Rebrand Aeolus as CloudForms Cloud Engine.
- cd3fdb3 Bump release, add changelog, 0.8.0-5

* Tue Jan 10 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-5
- becb88d Sanitize assembly name to prevent launch errors
- 50b4f0d Bump release, add changelog, 0.8.0-4

* Tue Jan 10 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-4
- b068c7d BZ#766929 - database.yml is world-readable
- 916d9f1 Bump release, add changelog, 0.8.0-3

* Tue Jan 10 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-3
- 981260f BZ#772682 Instance parameter values greater than 255 break deployment
- aa20e01 find_by_provider_name_and_login takes provider into account now

* Mon Jan 09 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-2
- 18ba534 Merge branch 'master' of github.com:aeolusproject/conductor
- 0a37767 API - Added template checking when creating an image
- 33d63a3 -change method of ensuring poolIds are unique, removed hard tab
- 4aa3fce updated deployment index refresh to categorize deployments by pool
- a2885b4 added pool ID to div identifier
- 0a020e7 Support for multiple accounts per provider.
- 6fa3ce3 Backbone will always use preset_filter value if present
- 5e068fe Bump release
- a18865d Update changelog entries
- 9c027cd Fix autoupdate with table filters
- 15c740b Adding 'No catalog' label when no catalog available for the deployable when creating image
- 0c98f1b Use a lambda to delay the evaluation of Provider in conjunction with scope
- d2a37e2 Reference lib/image by full path
- 342c552 Display a specific error message for image import with a blank ID
- a7ae8ec Add missing style to image import form
- 90826d7 Rename Catalog Entries to Deployables in the UI
- 55b28c5 update pools count with applying filters in pools table (bz770620)
- 5adcc24 Autoupdating pretty view fixed on Pools#index for multiline array of deployments
- 61934bc Fixing new deployable form
- fdd00ab Fixing failing rspec tests
- dd1d2db Localise instance count indicator in pretty view
- eea7d11 Fix the uptime format
- a627c74 BZ#755933 Last login,Last login IP fields empty.
- 46ac73e Added architecture check
- 7b24128 Removed duplicit vcr definition for aeolus-image
- df5f048 BZ 769635, added scope enabled to Provider and ProviderAccount
- 1853d01 Error displayed after provider destroy fails
- 810714c Redirect to catalog detail after catalog entry is created succesfully
- be4735d Fixing the date format in Deployment's json representation
- 188c848 Table striping fixed for autoupdating on the table view of pools#index
- fc0c339 Fixing autoupdating issues
- d23ed06 Fixed error rendering for AJAX requests
- 4c43e02 Fixing the permission partial
- f5d8de1 Error message fixed for creating new deployable without providing url for the xml
- d7d7a29 Deployable XML parsing switched to strict mode
- fe236fc BZ#766163 Add reboot_multiple to grid view of instances,controller method and localization.
- 0bae59e fix user dropdown in masthead

* Wed Jan 04 2012 Steve Linabery <slinaber@redhat.com> - 0.8.0-1
- d98cb57 Verify image exists before importing it from provider
- 314c90e Allow creating deployables from imported images
- b1e8993 Add realm selection to Deployment Overview
- b94664f Added support to DeployablesController to handle deployables without catalog
- 8d446e2 Fixing return_path in permissions#set_permission_object
- 4297b08 Change version of aeolus-image gem to 0.3.0
- 43440b1 Fixing jQuery template on deployments#show
- 9762232 Fixing autoupdate on deployments#show
- f1e6529 Prevent launching invalid deployments
- 77b349b Removed edit pool family button from pool families table (bz768154)
- a362758 Fix catalog dropdown when no catalog exist, bz769279
- cb5bf9b BZ 768089: Add model and UI for provider account priority
- e47d1a4 BZ 768089: spec test for provider account priority (revised)
- a3164ca BZ 768089: Refactor provider account matching to facilitate stubbing (revised)
- 93f464c Drop pretty/filter toggle from deployment details
- c3b896d Rake task to insert ldap users.
- 6512cb9 BZ 760901 - removed line touching unused lock file
- 02dfa3f fix for bz #765901: fix pools_in_use calculation
- 4f380bf new catalog entry from image, catalog select javascript
- 5be3de8 error messages in flash hud
- 3173e62 Replace description xml with name image import
- 77014ab Add a View Template XML option to Image Details
- 8668a57 BZ 767214 Removed the New Pool button from _section_header in pools controller
- 879c6eb catalog entries checkbox in header to enable select all listed catalog entries, catalog entries new_from_image i18n fix
- b062bc3 Fix message on launch from catalog
- 53ccabe pool_family_id param added to new_pool_path
- d5e79ff Deployable forms styling
- ab67147 Image import uses lib/image.rb class
- 0525111 Images#show properly detects ProviderAccount for imported image
- f0dea6c Fix failing RSpec tests
- a30691a images#show only shows the relevant provider for imported images
- 74143b3 API import (used by aeolus-cli) requires Provider Account now.
- c633f4c Image import is now linked to Provider Account, not just Provider
- 203b032 Log any errors encountered during image import
- 05f5067 Rescues a possible exception when creating a ProviderImage
- 04254b9 Hides build and upload buttons for imported images
- 72d9bf9 Image import uses new Image.import method
- b4019c2 fix afterdestroy callback for instance
- 003398f Fixed sort column
- 93d196a Fix deployable xml link on the launch overview page
- 415bddb Autoupdating deployments list on Pools#index
- 17c333b Show pool enabled/disabled status in Environments
- a211d72 added deployable name to create_from_image, BZ767109
- 725ad8f buildpush ui icons and styling
- d59142d Fix the pool families tests
- a20c7fd Add Images tab to the Pool Family details page
- 57afb0c Add "New Image" button to the images list
- 53548d1 Remove User Treatment from User form BZ767189
- 93d99a8 Fixed tests after removing warehouse models
- cd330fb Fixed deployable link
- c9c271a Removed warehouse models
- bf22438 Removed some methods from warehouse models
- 02d8dea Removed provider_images_for_image_list from image model
- 245fa3e Fix for bz #765907: change permissions tab label from 'Users' to 'Role Assignments'
- 057bf3b Fix missing translation on Import image button
- 4438a1a BZ#753917 Added target to API Build Output
- 926e1ac BZ#753917 Updated API to return Provider/Account on Push
- 547e1a5 Fixing jQuery template on deployments#show
- cf8cf19 Fixup for #761134
- 01e9383 Fixing recognize_path calls when the path contains prefix
- c784c3a Require a template file on the upload page
- cd06da9 Style Image Details' header buttons
- e15298b Don't display 'Download key' if there is not instance key
- 1b4af97 Fixup for bz761096
- 3ef5ea4 Quick Fix, destroy method is not called for ec2 and Mock instances, or if instance is in CREATE_FAILED state
- 34db60c new administer section navigation icons
- b196025 BUG-2751 - Delete instance on provider side when deleted in conductor
- ea32f34 rootpw param in template XML changed is now required
- 72fc9ac deployable details icons
- 859c1c1 fix launch deployable test
- 0978d61 deployable details Images part
- cec00a2 fixed bug with updating deployable xml
- c6dfc66 deployable details page styles, deployable details image section errors
- f31b995 Use names correctly on template upload
- 138d64d Input validation for new deployable from image
- 243d454 Fixing deployment card on Pools#index
- f11f6de Fix for bug #766038
- ef2c43d fix for BZ #761509: User quota and other stats
- 4c20a16 Allow changing deployment name on the Overview page
- c02a0c4 BZ761132 fix broken translations for template xml
- 32517e0 Fix flash message in images_controller#edit_xml
- 13f897e Disabling Add button if no available catalog exists
- ec56568 Condition added to XML validation in Deployable
- 4f813b4 Fixed deprecation warning in pool_families#edit
- 87cd77e Remove "load definition from XML" option from launch new deployment page
- a6ea1ef Replaced new_catalog_entry_path with new_deployable_path to work with new controller structure
- acd1159 Fixed a wrong regex on grep
- a37aaf5 Added rake task to verify the status of licenses in the project
- b7b467f Fixed list of catalog entries on deployables show page
- bc11e96 deployable detail styles and fixes through biuldpush ui
- 2c9a31d pool families list fix
- f23ac0c RM 2879 - Secondary method for creating provider accounts using a provider name instead of an id
- b24e67f BZ#754956 Return appropriate error code when parent not found
- 971aaf2 List of users added to permissions page
- ad124c6 Clean up Permission-related flash messages
- 972777f Add Build & Push to Deployable Details
- 978a43a Deploaybles and catalog_entries cleanups
- 03f7931 Redmine #2254: Always compile scss in dev enviroment.
- 122e55a Change sql statement to use rails helpers.
- 869c8a6 Fix this migration so it also works on sqlite.
- 077a18a Moving from GPL to ASL
- 3bd07b2 Add relp dependency to metapackage.
- 79e6dc9 bump version in Makefile and reset release
- 9fe1011 Add changelog and bump release on specfile for 0.7.0 RC

* Thu Dec 1 2011 Steve Linabery <slinaber@redhat.com> - 0.7.0-1
- 4178a0a Adds functionality to delete deployment configurations from config server
- cce4c7e Added pagination to events on instance detail page
- bf3868b Clean up minor unneeded test output.
- a9c520d Fixing aeolus-conductor.spec.in
- 0e2b2d4 format_value is more cautious with calling .split
- f35d2d7 Redmine #2515: Write and test actual logging behavior.
- 9a4be2b Redmine #2514: Write and test transformation of api data into correct log format.
- 3c1cc5c RM #2822: Add way to retrieve full list of attributes for validation.
- 2723e13 Comments out EventSpec for now
- d5f05a3 Rescue possibly-risky calls when creating a CDDR
- fc2cafa Fixing message for user creation
- 0167f7d Adding required fields indicator for user form
- c5c1b98 remove repeating sql statements in rails.log
- c239f6c Added build timestamp to image list view
- 32f5ea0 Updated images controller to use TemplateXML
- 1f447f4 Created TemplateXML model
- d86537c Correct bad call left after rubygem refactor
- af0ab18 Display the details for each image on the Deployable Details page
- 81a2c60 Event.rb uses full path to lib/aeolus/event
- 9df721a Fix for creating new Deployable page
- ad13160 Allow Deployable XML files to contain in-line configurations
- 42597dd Registering/deregistering multiple catalogs to deployment Renaming CatalogEntriesController to DeployablesController
- 35d6fef catalogs dropdown in Create new catalog entry from template, new catalog_entry form styling
- 79d5ab7 Buildpush layout
- fcc950a obscured launch parameter if it is password
- b0ed5b9 Update Image show UI
- c44778d Return provider cleanup content via API
- 2e3ead5 Updated Gemfile.lock for aeolus-image 0.2.0
- 7e068e9 Permissions page for deployables.
- a5ff27c Fixes failing test introduced by previous commit.
- 1aecfb4 Deployment flash error is no longer mashed together.
- 11b82d9 extracted apply_filters and apply_preset_filters methods to common_filter_methods module
- 01ab731 Cucumber tests for search and filters
- dd41e62 Added filter method, updated filters and search through the application
- ba22842 Added filters and search to tables through application
- 9016b1f Fixes bugs and warnings exposed by tests
- 4b78e5d Adds tests for Events
- 60e6245 lib/aeolus/event code is included in RPM and called for Events
- b86f1fd DBomatic does not write events; after-save hooks already handle this
- bd26168 InstanceObserver includes :status_code, :change_hash parameters to Event
- 3317495 Event model calls Event API after_create
- de655cf Define start_time and end_time for Deployment
- 8fc332f Remove secret_token.rb from conductor rpm - v2
- e36fa46 internationalize api error messages
- ae2cdf6 Fix pagginate on launch_from_catalog site
- a4b892b Image import GUI
- cecbf26 Fixes pool family detail, pools tab. Adds generic table instead of pool_families one
- 24fa151 BZ744713 - changed font styles for catalog images
- 99eda06 BZ#755933 Last login, Last login IP fields empty
- 5e1b27a Launch deployment from the Deployable Details page
- 8c8ae24 Correct bad call in Api::TargetImagesController
- 5d4d456 Updated API for new aeolus-image-rubygem changes
- 7da907f added reraising of BuildNotFound exception
- d2b1de1 changed return text to xml, add targets to import params
- f0d2b77 added reraising of ProviderImageNotFound expection
- 838179e API::ProviderImages spec, mock in #create + minor fixes
- ecacfa4 API::Images spec, minor xml fixes
- e3e193b API::Builds spec, minor return expectations fixes
- 2707489 API::TargetImages spec, #destroy
- b983da4 API::ProviderImages spec, #create #destroy
- 9f2c3e8 API::ImagesController spec, #create #destroy
- 9ee78b8 API::BuildsController spec #create #destroy
- 7b904f4 Display the backend provider image ID when deleted
- 6c7802e UI - create catalog entry from an image
- 2b43395 Removed unused rescue block when creating a template
- 56a2d9f Fix broken the Catalog Entries Cucumber feature
- eeac165 Add the skeleton for the Deployable Details page
- 131887d Add the name of belonging provider in provder_account#new/edit form
- 304c42b Change dropdown of catalogs to the name of belonging catalog in catalog_entry#new/edit form
- 6decf95 spec and cucumber changes for catalog_entry/deployable refactoring
- 1671422 view and controller changes for catalog_entry/deployable refactoring
- ff83dda Refactored catalog_entry model into catalog_entry and deployable models.
- 77dce31 Implementing pretty view for instances
- 4823c2b Changed aeolus user to 180:180 per bz 754274
- 0301070 dbomatic only writes instance events if they have changed
- 279331f Added options for creating catalog entry via upload XML or url to XML
- 0e7a2f9 Added tabs to catalog_entries#new form
- d88865d Fix tests after removing URL of catalog entry from launch form
- 4705924 Remove URL of catalog entry from launch UI
- bd41e3a Fixed specs and cukes after the change in catalog entries.
- 28e8fb8 Changes for catalog entry new/edit form.
- 39632a8 Added migration, that deletes URL attribute from catalog_entries and adds 2 column(xml, and xml_filename)
- 8e6f8dc Save template in warehouse
- d207889 Improved tests performance
- 65c7a75 Comments failing Image test
- 63903e6 Bump version number following imminent release of 0.6.0 from the 0.6.x branch
- 3a8a4d3 Updates ProviderType to use Rails 3 syntax
- f2f751b Add screens for template import
- 6f0b310 Fix spec so rpm builds.
- 690eb08 Task #2710 reboot of instance
- 62d2b4d Add initial 2 events to be sent.
- a6c4081 Initial Event API implementation.
- 57c4066 Added image detail page
- 78b505b Added images index view
- 6534ce1 Added empty images controller

* Tue Oct 04 2011 Maros Zatko <mzatko@redhat.com> - 0.4.0-1
- added controllers/api + views

* Thu Jul 21 2011 Mo Morsi <mmorsi@redhat.com> - 0.3.0-2
- update Source0 checkout instructions

* Wed Jul 20 2011 Mo Morsi <mmorsi@redhat.com> - 0.3.0-1
- new upstream release
- changes to conform to fedora guidelines

* Tue Apr 05 2011 Chris Lalancette <clalance@redhat.com> - 0.0.3-2
- Large spec file cleanup
- Split out development files into a -devel package
- Remove external dependencies and add to the aeolus-all package

* Thu Jan 20 2011 Chris Lalancette <clalance@redhat.com> - 0.0.3-1
- Rename from deltacloud-aggregator to aeolus-conductor

* Mon Sep 27 2010 Chris Lalancette <clalance@redhat.com> - 0.0.2-3
- Added new rubygem-parseconfig dependency
- Turn on services during install with chkconfig

* Sat Mar 6 2010 Ian Main <imain@redhat.com> - 0.0.2-2
- removed taskomatic from packaging.

* Wed Feb 18 2010 Mohammed Morsi <mmorsi@redhat.com> - 0.0.2-1
- renamed portal to aggregator
- updated / cleaned up package

* Fri Sep  1 2009  <sseago@redhat.com> - 0.0.1-1
- Initial build.