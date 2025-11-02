# PQC-Enabled CI Runner
# Provides liboqs and python-oqs for post-quantum cryptography testing
#
# Usage:
#   docker build -f .github/docker/pqc-runner.Dockerfile -t lukhas-pqc-runner .
#   docker run -it lukhas-pqc-runner python3 -c "import oqs; print(oqs.sig.algorithms())"

FROM python:3.11-slim

LABEL org.opencontainers.image.title="LUKHAS PQC Runner"
LABEL org.opencontainers.image.description="CI runner with liboqs and python-oqs for post-quantum cryptography"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/LukhasAI/Lukhas"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    ninja-build \
    libssl-dev \
    libssl3 \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install liboqs (Open Quantum Safe library)
ARG LIBOQS_VERSION=0.9.2
WORKDIR /tmp/liboqs-build

RUN wget -q https://github.com/open-quantum-safe/liboqs/archive/refs/tags/${LIBOQS_VERSION}.tar.gz \
    && tar -xzf ${LIBOQS_VERSION}.tar.gz \
    && cd liboqs-${LIBOQS_VERSION} \
    && mkdir build && cd build \
    && cmake -GNinja \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DOPENSSL_ROOT_DIR=/usr \
        -DBUILD_SHARED_LIBS=ON \
        -DOQS_BUILD_ONLY_LIB=ON \
        -DOQS_DIST_BUILD=ON \
        .. \
    && ninja \
    && ninja install \
    && ldconfig \
    && cd /tmp \
    && rm -rf /tmp/liboqs-build

# Verify liboqs installation
RUN ldconfig -p | grep liboqs

# Install Python cryptography dependencies
RUN pip install --no-cache-dir \
    cryptography>=41.0.0 \
    cffi>=1.15.0

# Install python-oqs (Python bindings for liboqs)
# Note: Use liboqs-python instead of pyoqs for better compatibility
ARG LIBOQS_PYTHON_VERSION=0.9.0
RUN pip install --no-cache-dir liboqs-python==${LIBOQS_PYTHON_VERSION}

# Install additional testing dependencies
RUN pip install --no-cache-dir \
    pytest>=7.4.0 \
    pytest-asyncio>=0.21.0 \
    pytest-cov>=4.1.0 \
    hypothesis>=6.82.0

# Create workspace directory
WORKDIR /workspace

# Smoke test: verify PQC algorithms are available
RUN python3 -c "import oqs; \
    print('Available signature algorithms:'); \
    for alg in oqs.sig.get_enabled_algorithms(): \
        print(f'  - {alg}'); \
    assert 'Dilithium2' in oqs.sig.get_enabled_algorithms(), 'Dilithium2 not available'"

# Performance benchmark script
COPY scripts/pqc/pqc_bench.py /usr/local/bin/pqc-bench

RUN chmod +x /usr/local/bin/pqc-bench

# Set environment variables for PQC
ENV LIBOQS_INSTALLED=1
ENV PQC_ENABLED=1

# Default command: show available algorithms
CMD ["python3", "-c", "import oqs; print('PQC Runner Ready'); print('Signature algorithms:', oqs.sig.get_enabled_algorithms())"]
