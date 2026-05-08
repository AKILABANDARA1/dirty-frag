FROM ubuntu:24.04

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    libcap2-bin \
    kmod \
    procps \
    iproute2 \
    util-linux

RUN pip3 install flask

# Create secure non-root user
RUN useradd -u 10001 -m tester

USER 10001

WORKDIR /home/tester

COPY app.py .

EXPOSE 8080

CMD ["python3", "app.py"]
