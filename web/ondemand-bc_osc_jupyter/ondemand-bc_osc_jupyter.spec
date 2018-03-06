# Disable debuginfo as it causes issues with bundled gems that build libraries
%global debug_package %{nil}
%global repo_name bc_osc_jupyter
%global app_name bc_osc_jupyter

Name:     ondemand-%{app_name}
Version:  0.4.1
Release:  1%{?dist}
Summary:  Batch Connect - OSC Jupyter Notebook

Group:    System Environment/Daemons
License:  MIT
URL:      https://github.com/OSC/%{repo_name}
Source0:  https://github.com/OSC/%{repo_name}/archive/v%{version}.tar.gz

Requires: ondemand

# Disable automatic dependencies as it causes issues with bundled gems and
# node.js packages used in the apps
AutoReqProv: no

%description
An interactive app designed for OSC OnDemand that launches a Jupyter Notebook server within an Owens batch job.


%prep
%setup -q -n %{repo_name}-%{version}


%build


%install
mkdir -p %{buildroot}%{_localstatedir}/www/ood/apps/sys/%{app_name}
if [ -x bin/setup ]; then
    bin/setup
fi
cp -a ./. %{buildroot}%{_localstatedir}/www/ood/apps/sys/%{app_name}/


%files
%defattr(-,root,root)
%{_localstatedir}/www/ood/apps/sys/%{app_name}
%{_localstatedir}/www/ood/apps/sys/%{app_name}/manifest.yml


%changelog
* Tue Mar 06 2018 Jeremy Nicklas <jnicklas@osc.edu> 0.4.1-1
- Bump bc_osc_jupyter to 0.4.1 (jnicklas@osc.edu)

* Tue Mar 06 2018 Jeremy Nicklas <jnicklas@osc.edu>
- Bump bc_osc_jupyter to 0.4.1 (jnicklas@osc.edu)

* Tue Feb 13 2018 Trey Dockendorf <tdockendorf@osc.edu> 0.3.0-1
- new package built with tito

