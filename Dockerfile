FROM ubuntu:24.04

RUN apt update && apt install -y \
    python3 \
    libcap2-bin \
    util-linux \
    procps \
    kmod \
    iproute2

RUN useradd -m tester

USER tester

WORKDIR /home/tester

COPY test.py .

CMD ["python3", "test.py"]
