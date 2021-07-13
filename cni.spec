Name     : cni
Version  : 0.8.0
Release  : 26
URL      : https://github.com/containernetworking/cni/
Source0  : https://github.com/containernetworking/cni/archive/v0.8.0.tar.gz
Summary  : Container Network Interface
Group    : Development/Tools
License  : Apache-2.0 BSD-3-Clause MIT MPL-2.0-no-copyleft-exception

BuildRequires : go

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true


%description
The CNI (Container Network Interface) project consists of
a specification and libraries for writing plugins to configure
network interfaces in Linux containers, along with a number
of supported plugins.

%prep
%setup -q


%build
set -e

ORG_PATH="github.com/containernetworking"
REPO_PATH="${ORG_PATH}/cni"

if [ ! -h gopath/src/${REPO_PATH} ]; then
	mkdir -p gopath/src/${ORG_PATH}
	ln -s ../../../.. gopath/src/${REPO_PATH} || exit 255
fi

export GO15VENDOREXPERIMENT=1
export GO111MODULE=auto
export GOPATH=${PWD}/gopath
BUILDFLAGS="-buildmode=pie -v"

echo "Building API"
go build $BUILDFLAGS "$@" ${REPO_PATH}/libcni

echo "Building reference CLI"
go build $BUILDFLAGS -o ${PWD}/bin/cnitool "$@" ${REPO_PATH}/cnitool

echo "Building plugins"
PLUGINS="plugins/test/*"
for d in $PLUGINS; do
	if [ -d $d ]; then
		plugin=$(basename $d)
		echo "  " $plugin
		go build $BUILDFLAGS -o ${PWD}/bin/$plugin "$@" ${REPO_PATH}/$d
	fi
done

%install
# these binaries are not supposed to be run by users
install -d  %{buildroot}/usr/libexec/cni
for f in $(ls ./bin); do
    install -p -m 0755 "./bin/${f}" %{buildroot}/usr/libexec/cni
done


%files
%defattr(-,root,root,-)
/usr/libexec/cni/cnitool
/usr/libexec/cni/noop
/usr/libexec/cni/sleep
