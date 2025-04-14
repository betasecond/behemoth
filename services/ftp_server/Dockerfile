FROM alpine:latest

# Install vsftpd
RUN apk add --no-cache vsftpd

# Create a user for FTP login
RUN adduser -D -h /home/testuser testuser && \
    echo "testuser:testpass" | chpasswd

# Create content directory
RUN mkdir -p /home/testuser/files && \
    chown -R testuser:testuser /home/testuser && \
    echo "Welcome to the FTP server!" > /home/testuser/files/welcome.txt

# Configure vsftpd
RUN echo "listen=YES" > /etc/vsftpd/vsftpd.conf && \
    echo "anonymous_enable=NO" >> /etc/vsftpd/vsftpd.conf && \
    echo "local_enable=YES" >> /etc/vsftpd/vsftpd.conf && \
    echo "write_enable=YES" >> /etc/vsftpd/vsftpd.conf && \
    echo "local_umask=022" >> /etc/vsftpd/vsftpd.conf && \
    echo "dirmessage_enable=YES" >> /etc/vsftpd/vsftpd.conf && \
    echo "connect_from_port_20=YES" >> /etc/vsftpd/vsftpd.conf && \
    echo "pasv_enable=YES" >> /etc/vsftpd/vsftpd.conf && \
    echo "pasv_min_port=40000" >> /etc/vsftpd/vsftpd.conf && \
    echo "pasv_max_port=40100" >> /etc/vsftpd/vsftpd.conf && \
    echo "seccomp_sandbox=NO" >> /etc/vsftpd/vsftpd.conf

# Expose FTP ports
EXPOSE 21 40000-40100

CMD ["vsftpd", "/etc/vsftpd/vsftpd.conf"]