# hipSOLVER thin HIP wrapper over rocSOLVER (TheRock 7.14)

Name:		hipsolver
Version:	7.14.0
Release:	1
Summary:	HIP dense linear algebra solvers (rocSOLVER wrapper)
License:	MIT
Group:		System/Libraries
URL:		https://github.com/ROCm/rocm-libraries
Source0:	https://github.com/ROCm/rocm-libraries/releases/download/therock-7.14/hipsolver.tar.gz#/hipsolver-%{version}.tar.gz
# Clang 23 freestanding: memcpy needs <cstring>
Patch0:		0001-include-cstring-sparse.patch
# Honor -DLAPACK_LIBRARIES= (skip netlib CONFIG static .a overwrite)
Patch1:		0002-honor-preset-lapack-libraries.patch

BuildRequires:	rocm-rpm-macros
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	rocm-cmake
BuildRequires:	hipcc
BuildRequires:	rocm-hip-devel
BuildRequires:	clang >= %{rocm_llvm_maj_ver}
BuildRequires:	rocsolver-devel
BuildRequires:	rocblas-devel
# Shared OpenBLAS for host geev fallback (netlib .a fails under clang LTO)
BuildRequires:	lib64openblas-devel
BuildRequires:	python3

ExclusiveArch:	%{x86_64} %{aarch64}

%description
hipSOLVER is a thin HIP API wrapper over rocSOLVER. Sparse path uses
dlopen stubs when built without SuiteSparse/rocSPARSE at build time.

%package devel
Summary:	Development files for hipsolver
Group:		Development/C++
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	rocm-hip-devel
Requires:	rocsolver-devel
Provides:	hipsolver-devel = %{EVRD}

%description devel
Headers and CMake package for hipsolver.

%prep
%autosetup -n hipsolver -p1

export CXX=hipcc
export CC=clang
export ROCM_PATH=%{_prefix}
export HIP_PATH=%{_prefix}
CXXFLAGS=$(printf '%s' "%{optflags}" | sed -E 's/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')
export CXXFLAGS
export CFLAGS="$CXXFLAGS"
export LDFLAGS=$(printf '%s' "%{?__global_ldflags}" | sed -E 's/-mfpmath=[^ ]+//g; s/ -m[a-z0-9+.=]+//g')
%cmake %{rocm_cmake_fhs} %{rocm_cmake_gpu_targets_blas} \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_CXX_COMPILER=hipcc \
	-DCMAKE_CXX_FLAGS="$CXXFLAGS" \
	-DBUILD_SHARED_LIBS=ON \
	-DBUILD_WITH_SPARSE=OFF \
	-DBUILD_FORTRAN_BINDINGS=OFF \
	-DEXPORT_FORTRAN_BINDINGS=OFF \
	-DBUILD_CLIENTS_TESTS=OFF \
	-DBUILD_CLIENTS_BENCHMARKS=OFF \
	-DBUILD_CLIENTS_SAMPLES=OFF \
	-DBUILD_HIPBLAS_TESTS=OFF \
	-DBUILD_HIPSPARSE_TESTS=OFF \
	-DHIPSOLVER_INTERNAL_LAPACK_BUILD=OFF \
	-DLAPACK_LIBRARIES=/usr/lib64/libopenblas.so \
	-DBLAS_LIBRARIES=/usr/lib64/libopenblas.so \
	-DROCM_PATH=%{_prefix} \
	-DCMAKE_PREFIX_PATH=%{_prefix} \
	-G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build
if [ -d %{buildroot}/usr/lib/cmake/hipsolver ] && [ ! -d %{buildroot}%{_libdir}/cmake/hipsolver ]; then
	mkdir -p %{buildroot}%{_libdir}/cmake
	mv %{buildroot}/usr/lib/cmake/hipsolver %{buildroot}%{_libdir}/cmake/
	rmdir %{buildroot}/usr/lib/cmake 2>/dev/null || true
	rmdir %{buildroot}/usr/lib 2>/dev/null || true
fi

%files
%license LICENSE.md
%doc README.md
%exclude %{_docdir}/hipsolver/LICENSE.md
%{_libdir}/libhipsolver.so.*

%files devel
%{_includedir}/hipsolver/
%{_libdir}/libhipsolver.so
%{_libdir}/cmake/hipsolver/
