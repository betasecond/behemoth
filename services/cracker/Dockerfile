FROM ubuntu:20.04

# Set noninteractive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

# Install hashcat and required dependencies
RUN apt-get update && apt-get install -y \
    hashcat \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r nonroot && \
    useradd -r -g nonroot -d /home/nonroot -m nonroot

# Set up data directory with appropriate permissions
RUN mkdir -p /data && chown -R nonroot:nonroot /data

# Set workdir
WORKDIR /data

# Switch to non-root user
USER nonroot

CMD ["sleep", "infinity"]