Summary: WPA/WPA2/IEEE 802.1X Supplicant
Name: wpa_supplicant
Epoch: 1
Version: 0.6.8
Release: 10%{?dist}
License: BSD
Group: System Environment/Base
Source0: http://hostap.epitest.fi/releases/%{name}-%{version}.tar.gz
Source1: %{name}.config
Source2: %{name}.conf
Source3: %{name}.init.d
Source4: %{name}.sysconfig
Source6: %{name}.logrotate

%define build_gui 1
%if 0%{?rhel} >= 1
%define build_gui 0
%endif

%if %{build_gui}
%define with_qt4 0
%if 0%{?fedora} >= 14
%define with_qt4 1
%endif
%endif

Patch0: wpa_supplicant-assoc-timeout.patch
Patch1: wpa_supplicant-0.5.7-qmake-location.patch
Patch2: wpa_supplicant-0.5.7-flush-debug-output.patch
Patch4: wpa_supplicant-0.5.10-dbus-service-file.patch
Patch5: wpa_supplicant-0.6.7-quiet-scan-results-message.patch
Patch6: wpa_supplicant-0.6.8-disconnect-fixes.patch
Patch7: wpa_supplicant-0.6.8-disconnect-init-deinit.patch
Patch8: wpa_supplicant-0.6.8-handle-driver-disconnect-spam.patch
Patch9: wpa_supplicant-0.6.8-ap-stability.patch
Patch10: wpa_supplicant-0.6.8-scanning-property.patch
Patch11: wpa_supplicant-0.6.9-scan-faster.patch
Patch12: wpa_supplicant-0.6.9-eapol-race-fix.patch
Patch13: wpa_supplicant-0.6.8-openssl-init.patch
Patch20: wpa_supplicant-0.6.8-gui-qt4.patch

URL: http://w1.fi/wpa_supplicant/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{build_gui}
%if %{with_qt4}
BuildRequires: qt-devel >= 4.0
%else
BuildRequires: qt3-devel
%endif
%endif
BuildRequires: openssl-devel
BuildRequires: readline-devel
BuildRequires: dbus-devel

%description
wpa_supplicant is a WPA Supplicant for Linux, BSD and Windows with support 
for WPA and WPA2 (IEEE 802.11i / RSN). Supplicant is the IEEE 802.1X/WPA 
component that is used in the client stations. It implements key negotiation 
with a WPA Authenticator and it controls the roaming and IEEE 802.11 
authentication/association of the wlan driver.

%if %{build_gui}

%package gui
Summary: Graphical User Interface for %{name}
Group: Applications/System

%description gui
Graphical User Interface for wpa_supplicant written using QT

%endif

%prep
%setup -q
%patch0 -p1 -b .assoc-timeout
%patch1 -p1 -b .qmake-location
%patch2 -p1 -b .flush-debug-output
%patch4 -p1 -b .dbus-service-file
%patch5 -p1 -b .quiet-scan-results-msg
%patch6 -p1 -b .really-disassoc
%patch7 -p1 -b .disconnect-init-deinit
%patch8 -p1 -b .disconnect-spam
%patch9 -p1 -b .ap-stability
%patch10 -p1 -b .scanning-property
%patch11 -p1 -b .scan-faster
%patch12 -p1 -b .eapol-race-fix
%patch13 -p1 -b .more-openssl-algs
%patch20 -p1 -b .qt4

%build
pushd wpa_supplicant
  cp %{SOURCE1} ./.config
  CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ;
  CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS ;
  make %{_smp_mflags}
%if %{build_gui}
%if %{with_qt4}
  QTDIR=%{_libdir}/qt4 make wpa_gui-qt4 %{_smp_mflags}
%else
  QTDIR=%{_libdir}/qt-3.3 make wpa_gui %{_smp_mflags}
%endif
%endif
popd

%install
rm -rf %{buildroot}

# init scripts
install -d %{buildroot}/%{_sysconfdir}/rc.d/init.d
install -d %{buildroot}/%{_sysconfdir}/sysconfig
install -m 0755 %{SOURCE3} %{buildroot}/%{_sysconfdir}/rc.d/init.d/%{name}
install -m 0644 %{SOURCE4} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}
install -d %{buildroot}/%{_sysconfdir}/logrotate.d
install -m 0644 %{SOURCE6} %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}

# config
install -d %{buildroot}/%{_sysconfdir}/%{name}
install -m 0600 %{SOURCE2} %{buildroot}/%{_sysconfdir}/%{name}

# binary
install -d %{buildroot}/%{_sbindir}
install -m 0755 %{name}/wpa_passphrase %{buildroot}/%{_sbindir}
install -m 0755 %{name}/wpa_cli %{buildroot}/%{_sbindir}
install -m 0755 %{name}/wpa_supplicant %{buildroot}/%{_sbindir}
install -d %{buildroot}/%{_sysconfdir}/dbus-1/system.d/
install -m 0644 %{name}/dbus-wpa_supplicant.conf %{buildroot}/%{_sysconfdir}/dbus-1/system.d/wpa_supplicant.conf
install -d %{buildroot}/%{_datadir}/dbus-1/system-services/
install -m 0644 %{name}/dbus-wpa_supplicant.service %{buildroot}/%{_datadir}/dbus-1/system-services/fi.epitest.hostap.WPASupplicant.service

%if %{build_gui}
# gui
install -d %{buildroot}/%{_bindir}
%if %{with_qt4}
install -m 0755 %{name}/wpa_gui-qt4/wpa_gui %{buildroot}/%{_bindir}
%else
install -m 0755 %{name}/wpa_gui/wpa_gui %{buildroot}/%{_bindir}
%endif
%endif

# running
mkdir -p %{buildroot}/%{_localstatedir}/run/%{name}

# man pages
install -d %{buildroot}%{_mandir}/man{5,8}
install -m 0644 %{name}/doc/docbook/*.8 %{buildroot}%{_mandir}/man8
install -m 0644 %{name}/doc/docbook/*.5 %{buildroot}%{_mandir}/man5

# some cleanup in docs
rm -f  %{name}/doc/.cvsignore
rm -rf %{name}/doc/docbook


%clean
rm -rf %{buildroot}

%post
if [ $1 = 1 ]; then
	chkconfig --add %{name}
fi

%preun
if [ $1 = 0 ]; then
	service %{name} stop > /dev/null 2>&1
	killall -TERM wpa_supplicant >/dev/null 2>&1
	/sbin/chkconfig --del %{name}
fi


%files
%defattr(-, root, root)
%doc COPYING %{name}/ChangeLog README %{name}/eap_testing.txt %{name}/todo.txt %{name}/wpa_supplicant.conf %{name}/examples
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_sysconfdir}/rc.d/init.d/%{name}
%{_sysconfdir}/dbus-1/system.d/%{name}.conf
%{_datadir}/dbus-1/system-services/fi.epitest.hostap.WPASupplicant.service
%{_sbindir}/wpa_passphrase
%{_sbindir}/wpa_supplicant
%{_sbindir}/wpa_cli
%dir %{_localstatedir}/run/%{name}
%dir %{_sysconfdir}/%{name}
%{_mandir}/man8/*
%{_mandir}/man5/*

%if %{build_gui}
%files gui
%defattr(-, root, root)
%{_bindir}/wpa_gui
%endif

%changelog
* Thu May 13 2010 Dan Williams <dcbw@redhat.com> - 1:0.6.8-10
- Remove prereq on chkconfig
- Build GUI with qt4 for rawhide (rh #537105)

* Thu May  6 2010 Dan Williams <dcbw@redhat.com> - 1:0.6.8-9
- Fix crash when interfaces are removed (like suspend/resume) (rh #589507)

* Wed Jan  6 2010 Dan Williams <dcbw@redhat.com> - 1:0.6.8-8
- Fix handling of newer PKCS#12 files (rh #541924)

* Sun Nov 29 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.8-7
- Fix supplicant initscript return value (rh #521807)
- Fix race when connecting to WPA-Enterprise/802.1x-enabled access points (rh #508509)
- Don't double-scan when attempting to associate

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1:0.6.8-6
- rebuilt with new openssl

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.6.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed May 13 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.8-4
- Let D-Bus clients know when the supplicant is scanning

* Tue May 12 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.8-3
- Ensure the supplicant starts and ends with clean driver state
- Handle driver disconnect spammage by forcibly clearing SSID
- Don't switch access points unless the current association is dire (rh #493745)

* Tue May 12 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.8-2
- Avoid creating bogus Ad-Hoc networks when forcing the driver to disconnect (rh #497771)

* Mon Mar  9 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.8-1
- Update to latest upstream release

* Wed Feb 25 2009 Colin Walters <walters@verbum.org> - 1:0.6.7-4
- Add patch from upstream to suppress unrequested replies, this
  quiets a dbus warning.

* Fri Feb  6 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.7-3
- Fix scan result retrieval in very dense wifi environments

* Fri Feb  6 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.7-2
- Ensure that drivers don't retry association when they aren't supposed to

* Fri Jan 30 2009 Dan Williams <dcbw@redhat.com> - 1:0.6.7-1
- Fix PEAP connections to Windows Server 2008 authenticators (rh #465022)
- Stop supplicant on uninstall (rh #447843)
- Suppress scan results message in logs (rh #466601)

* Sun Jan 18 2009 Tomas Mraz <tmraz@redhat.com> - 1:0.6.4-3
- rebuild with new openssl

* Mon Oct 15 2008 Dan Williams <dcbw@redhat.com> - 1:0.6.4-2
- Handle encryption keys correctly when switching 802.11 modes (rh #459399)
- Better scanning behavior on resume from suspend/hibernate
- Better interaction with newer kernels and drivers

* Wed Aug 27 2008 Dan Williams <dcbw@redhat.com> - 1:0.6.4-1
- Update to 0.6.4
- Remove 'hostap', 'madwifi', and 'prism54' drivers; use standard 'wext' instead
- Drop upstreamed patches

* Tue Jun 10 2008 Dan Williams <dcbw@redhat.com> - 1:0.6.3-6
- Fix 802.11a frequency bug
- Always schedule specific SSID scans to help find hidden APs
- Properly switch between modes on mac80211 drivers
- Give adhoc connections more time to assocate

* Mon Mar 10 2008 Christopher Aillon <caillon@redhat.com> - 1:0.6.3-5
- BuildRequires qt3-devel

* Sat Mar  8 2008 Dan Williams <dcbw@redhat.com> - 1:0.6.3-4
- Fix log file path in service config file

* Thu Mar  6 2008 Dan Williams <dcbw@redhat.com> - 1:0.6.3-3
- Don't start the supplicant by default when installed (rh #436380)

* Tue Mar  4 2008 Dan Williams <dcbw@redhat.com> - 1:0.6.3-2
- Fix a potential use-after-free in the D-Bus byte array demarshalling code

* Mon Mar  3 2008 Dan Williams <dcbw@redhat.com> - 1:0.6.3-1
- Update to latest development release; remove upstreamed patches

* Fri Feb 22 2008 Dan Williams <dcbw@redhat.com> 1:0.5.7-23
- Fix gcc 4.3 rebuild issues

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1:0.5.7-22
- Autorebuild for GCC 4.3

* Tue Dec 25 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-21
- Backport 'frequency' option for Ad-Hoc network configs

* Mon Dec 24 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-20
- Fix LSB initscript header to ensure 'messagebus' is started first (rh #244029)

* Thu Dec  6 2007 Dan Williams <dcbw@redhat.com> - 1:0.5.7-19
- Fix two leaks when signalling state and scan results (rh #408141)
- Add logrotate config file (rh #404181)
- Add new LSB initscript header to initscript with correct deps (rh #244029)
- Move other runtime arguments to /etc/sysconfig/wpa_supplicant
- Start after messagebus service (rh #385191)
- Fix initscript 'condrestart' command (rh #217281)

* Tue Dec  4 2007 Matthias Clasen <mclasen@redhat.com> - 1:0.5.7-18
- Rebuild against new openssl

* Tue Dec  4 2007 Ville Skyttä <ville.skytta at iki.fi> - 1:0.5.7-17
- Group: Application/System -> Applications/System in -gui.

* Tue Nov 13 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-16
- Add IW_ENCODE_TEMP patch for airo driver and Dynamic WEP
- Fix error in wpa_supplicant-0.5.7-ignore-dup-ca-cert-addition.patch that
    caused the last error to not be printed
- Fix wpa_supplicant-0.5.7-ignore-dup-ca-cert-addition.patch to ignore
    duplicate cert additions for all certs and keys
- Change license to BSD due to linkage against OpenSSL since there is no
    OpenSSL exception in the GPLv2 license text that upstream ships

* Sun Oct 28 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-15
- Fix Dynamic WEP associations with mac80211-based drivers

* Sun Oct 28 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-14
- Don't error an association on duplicate CA cert additions

* Wed Oct 24 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-13
- Correctly set the length of blobs added via the D-Bus interface

* Wed Oct 24 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-12
- Fix conversion of byte arrays to strings by ensuring the buffer is NULL
    terminated after conversion

* Sat Oct 20 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-11
- Add BLOB support to the D-Bus interface
- Fix D-Bus interface permissions so that only root can use the wpa_supplicant
    D-Bus interface

* Tue Oct  9 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-10
- Don't segfault with dbus control interface enabled and invalid network
    interface (rh #310531)

* Tue Sep 25 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-9
- Always allow explicit wireless scans triggered from a control interface

* Thu Sep 20 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-8
- Change system bus activation file name to work around D-Bus bug that fails
    to launch services unless their .service file is named the same as the
    service itself

* Fri Aug 24 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-7
- Make SIGUSR1 change debug level on-the-fly; useful in combination with
    the -f switch to log output to /var/log/wpa_supplicant.log
- Stop stripping binaries on install so we get debuginfo packages
- Remove service start requirement for interfaces & devices from sysconfig file,
    since wpa_supplicant's D-Bus interface is now turned on

* Fri Aug 17 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-6
- Fix compilation with RPM_OPT_FLAGS (rh #249951)
- Make debug output to logfile a runtime option

* Fri Aug 17 2007 Christopher Aillon <caillon@redhat.com> - 0.5.7-5
- Update the license tag

* Tue Jun 19 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-4
- Fix initscripts to use -Dwext by default, be more verbose on startup
    (rh #244511)

* Mon Jun  4 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-3
- Fix buffer overflow by removing syslog patch (#rh242455)

* Mon Apr  9 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-2
- Add patch to send output to syslog

* Thu Mar 15 2007 Dan Williams <dcbw@redhat.com> - 0.5.7-1
- Update to 0.5.7 stable release

* Mon Oct 27 2006 Dan Williams <dcbw@redhat.com> - 0.4.9-1
- Update to 0.4.9 for WE-21 fixes, remove upstreamed patches
- Don't package doc/ because they aren't actually wpa_supplicant user documentation,
    and becuase it pulls in perl

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.4.8-10.1
- rebuild

* Thu Apr 27 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-10
- Add fix for madwifi and WEP (wpa_supplicant/hostap bud #140) (#rh190075#)
- Fix up madwifi-ng private ioctl()s for r1331 and later
- Update madwifi headers to r1475

* Tue Apr 25 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-9
- Enable Wired driver, PKCS12, and Smartcard options (#rh189805#)

* Tue Apr 11 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-8
- Fix control interface key obfuscation a bit

* Sun Apr  2 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-7
- Work around older & incorrect drivers that return null-terminated SSIDs

* Mon Mar 27 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-6
- Add patch to make orinoco happy with WEP keys
- Enable Prism54-specific driver
- Disable ipw-specific driver; ipw2x00 should be using WEXT instead

* Fri Mar  3 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-5
- Increase association timeout, mainly for drivers that don't
	fully support WPA ioctls yet

* Fri Mar  3 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-4
- Add additional BuildRequires #rh181914#
- Add prereq on chkconfig #rh182905# #rh182906#
- Own /var/run/wpa_supplicant and /etc/wpa_supplicant #rh183696#

* Wed Mar  1 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-3
- Install wpa_passphrase too #rh183480#

* Mon Feb 27 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-2
- Don't expose private data on the control interface unless requested

* Fri Feb 24 2006 Dan Williams <dcbw@redhat.com> - 0.4.8-1
- Downgrade to 0.4.8 stable release rather than a dev release

* Sun Feb 12 2006 Dan Williams <dcbw@redhat.com> - 0.5.1-3
- Documentation cleanup (Terje Rosten <terje.rosten@ntnu.no>)

* Sun Feb 12 2006 Dan Williams <dcbw@redhat.com> - 0.5.1-2
- Move initscript to /etc/rc.d/init.d

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.5.1-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.5.1-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sun Feb  5 2006 Dan Williams <dcbw@redhat.com> 0.5.1-1
- Update to 0.5.1
- Add WE auth fallback to actually work with older drivers

* Thu Jan 26 2006 Dan Williams <dcbw@redhat.com> 0.4.7-2
- Bring package into Fedora Core
- Add ap_scan control interface patch
- Enable madwifi-ng driver

* Sun Jan 15 2006 Douglas E. Warner <silfreed@silfreed.net> 0.4.7-1
- upgrade to 0.4.7
- added package w/ wpa_gui in it

* Mon Nov 14 2005 Douglas E. Warner <silfreed@silfreed.net> 0.4.6-1
- upgrade to 0.4.6
- adding ctrl interface changes recommended 
  by Hugo Paredes <hugo.paredes@e-know.org>

* Sun Oct  9 2005 Douglas E. Warner <silfreed@silfreed.net> 0.4.5-1
- upgrade to 0.4.5
- updated config file wpa_supplicant is built with
  especially, the ipw2100 driver changed to just ipw
  and enabled a bunch more EAP
- disabled dist tag

* Thu Jun 30 2005 Douglas E. Warner <silfreed@silfreed.net> 0.4.2-3
- fix typo in init script

* Thu Jun 30 2005 Douglas E. Warner <silfreed@silfreed.net> 0.4.2-2
- fixing init script using fedora-extras' template
- removing chkconfig default startup

* Tue Jun 21 2005 Douglas E. Warner <silfreed@silfreed.net> 0.4.2-1
- upgrade to 0.4.2
- new sample conf file that will use any unrestricted AP
- make sysconfig config entry
- new BuildRoot for Fedora Extras
- adding dist tag to Release

* Fri May 06 2005 Douglas E. Warner <silfreed@silfreed.net> 0.3.8-1
- upgrade to 0.3.8

* Thu Feb 10 2005 Douglas E. Warner <silfreed@silfreed.net> 0.3.6-2
- compile ipw driver in

* Wed Feb 09 2005 Douglas E. Warner <silfreed@silfreed.net> 0.3.6-1
- upgrade to 0.3.6

* Thu Dec 23 2004 Douglas E. Warner <silfreed@silfreed.net> 0.2.5-4
- fixing init script

* Mon Dec 20 2004 Douglas E. Warner <silfreed@silfreed.net> 0.2.5-3
- fixing init script
- adding post/preun items to add/remove via chkconfig

* Mon Dec 20 2004 Douglas E. Warner <silfreed@silfreed.net> 0.2.5-2
- adding sysV scripts

* Mon Dec 20 2004 Douglas E. Warner <silfreed@silfreed.net> 0.2.5-1
- Initial RPM release.

