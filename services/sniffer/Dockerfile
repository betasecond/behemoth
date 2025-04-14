FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install tshark (Wireshark CLI) and other utilities
RUN apt-get update && apt-get install -y \
    tshark \
    iproute2 \
    net-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r nonroot && \
    useradd -r -g nonroot -d /home/nonroot -m nonroot

# Set up pcap directory with appropriate permissions
RUN mkdir -p /pcap && chown -R nonroot:nonroot /pcap

# Set workdir
WORKDIR /pcap

# Add wireshark group and add nonroot to it to allow capturing packets
RUN groupadd -r wireshark && \
    usermod -a -G wireshark nonroot && \
    chgrp wireshark /usr/bin/dumpcap && \
    chmod 750 /usr/bin/dumpcap && \
    setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap

# Switch to non-root user
USER nonroot

CMD ["sleep", "infinity"]