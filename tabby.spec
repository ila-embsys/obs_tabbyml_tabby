#
# spec file for package tabby
#

Name:           tabby
Version:        0
Release:        0
Summary:        A self-hosted AI coding assistant 

License:        Apache-2.0
Url:            https://github.com/TabbyML/tabby

Source0:        %{name}-%{version}.tar.gz
Source1:        vendor.tar.zst
Source2:        %{name}.default.config.toml

Patch0:         vulkan-llama-ggml.patch

BuildRequires:  cargo-packaging
BuildRequires:  pkgconfig(openssl)
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  shaderc

# Not available
# BuildRequires:  pkgconfig(CUDAToolkit)

# Git is required for rust's vergen, but package source doesn't contain
# git information, so adding it changes nothing
# BuildRequires:  git

%description
Opensource, self-hosted AI coding assistant

%package devel
Summary:        tabby development files

%description devel
Those are the development files tabby

%prep
%setup
tar -xf %{_sourcedir}/vendor.tar.zst --directory .
patch -p1 < %{_sourcedir}/vulkan-llama-ggml.patch

%build

# Imitate rust's vergen git variable
export VERGEN_GIT_DESCRIBE=v%{version}

# The build arguments taken from original docker/Dockerfile.cuda
# the -release flag is stripped down due to
# cargo_build macro already contains it
#
# Here could be also rocm feature but llama-cpp-server build process tries
# to use /opt/rocm/llvm/build/clang that doesn't exist so disable for now
#
# Cuda is disabled due to no pkgconfig(CUDAToolkit) available
%{cargo_build} --no-default-features --features vulkan,prod --package %{name}

%install
%{__install} -m755 -d %{buildroot}%{_bindir}
%{__install} -m755 target/release/%{name} %{buildroot}/%{_bindir}/%{name}
%{__install} -m755 target/release/llama-server %{buildroot}/%{_bindir}/llama-server

%{__install} -m755 -d %{buildroot}/%{_sysconfdir}/%{name}
%{__install} -m644 %{_sourcedir}/%{name}.default.config.toml %{buildroot}/%{_sysconfdir}/%{name}/config.toml

%{__install} -m755 -d %{buildroot}/%{_unitdir}
%{__install} -m644 %{_sourcedir}/%{name}.service %{buildroot}%{_unitdir}

%{__install} -m755 -d %{buildroot}/%{_sharedstatedir}/%{name}

# Will not work without internet access
# %check

%files
%{_bindir}/%{name}
%{_bindir}/llama-server
%{_unitdir}/%{name}.service

%{_sysconfdir}/%{name} 
%config(noreplace) %{_sysconfdir}/%{name}/config.toml

%{_sharedstatedir}/%{name}

%license LICENSE
%doc README.md

%pre
ln -s %{_sysconfdir}/%{name}/config.toml -t %{_sharedstatedir}/%{name} || true
%service_add_pre %{name}.service

%post
%service_add_post %{name}.service

%preun
%service_del_preun %{name}.service

%postun
%service_del_postun %{name}.service

%changelog
