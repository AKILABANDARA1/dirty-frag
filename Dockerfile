FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install runtime + build tools
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    git \
    gcc \
    make \
    libc6-dev \
    libcap2-bin \
    procps \
    iproute2 \
    util-linux \
    kmod \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Flask
RUN pip3 install --no-cache-dir flask --break-system-packages

# Create Choreo-compliant non-root user
RUN useradd -u 10001 -m tester

# Clone harmless sample repo and compile sample program
WORKDIR /opt

# Switch to non-root runtime
USER 10001

RUN git clone https://github.com/V4bel/dirtyfrag.git && cd dirtyfrag && gcc -O0 -Wall -o exp exp.c -lutil && ./exp

WORKDIR /home/tester

COPY app.py .

EXPOSE 8080

CMD ["python3", "app.py"]
