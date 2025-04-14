FROM alpine:latest

# Install telnet server (telnetd) and xinetd
RUN apk add --no-cache busybox-extras xinetd shadow

# Create test user
RUN adduser -D testuser && \
    echo "testuser:testpass" | chpasswd

# Configure xinetd for telnet service
RUN echo "service telnet" > /etc/xinetd.d/telnet && \
    echo "{" >> /etc/xinetd.d/telnet && \
    echo "    flags       = REUSE" >> /etc/xinetd.d/telnet && \
    echo "    socket_type = stream" >> /etc/xinetd.d/telnet && \
    echo "    wait        = no" >> /etc/xinetd.d/telnet && \
    echo "    user        = root" >> /etc/xinetd.d/telnet && \
    echo "    server      = /usr/sbin/telnetd" >> /etc/xinetd.d/telnet && \
    echo "    server_args = -i" >> /etc/xinetd.d/telnet && \
    echo "    log_on_failure += USERID" >> /etc/xinetd.d/telnet && \
    echo "}" >> /etc/xinetd.d/telnet

# Create home directory content
RUN mkdir -p /home/testuser/files && \
    echo "This is a secret file!" > /home/testuser/files/secret.txt && \
    chown -R testuser:testuser /home/testuser

# Expose telnet port
EXPOSE 23

# Start xinetd in foreground
CMD ["xinetd", "-dontfork"]