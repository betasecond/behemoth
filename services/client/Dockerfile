FROM alpine:latest

# Install client tools
RUN apk add --no-cache \
    ftp \
    busybox-extras \
    curl \
    netcat-openbsd \
    tcpdump \
    nmap \
    bash

# Create user directory
RUN mkdir -p /home/attacker

WORKDIR /home/attacker

# Create a simple script to help with testing
RUN echo '#!/bin/bash\n\
echo "Behemoth Attacker Client"\n\
echo "Available commands:"\n\
echo "  1. Connect to FTP: ftp ftp_service"\n\
echo "  2. Connect to Telnet: telnet telnet_service"\n\
echo "  3. Auto FTP login: auto_ftp.sh"\n\
echo "  4. Auto Telnet login: auto_telnet.sh"\n\
' > /home/attacker/help.sh && chmod +x /home/attacker/help.sh

# Create auto-login scripts
RUN echo '#!/bin/bash\n\
echo "Connecting to FTP server and logging in automatically..."\n\
echo -e "user testuser\\npass testpass\\nls\\nquit" | ftp ftp_service\n\
' > /home/attacker/auto_ftp.sh && chmod +x /home/attacker/auto_ftp.sh

RUN echo '#!/bin/bash\n\
echo "Connecting to Telnet server and logging in automatically..."\n\
echo -e "testuser\\ntestpass\\nls\\nexit" | telnet telnet_service\n\
' > /home/attacker/auto_telnet.sh && chmod +x /home/attacker/auto_telnet.sh

CMD ["/bin/bash"]