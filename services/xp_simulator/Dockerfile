FROM alpine:latest

# Create non-root user for security
RUN addgroup -S appgroup && adduser -S -G appgroup appuser

# Create data directory
RUN mkdir -p /data && chown -R appuser:appgroup /data

# Switch to non-root user
USER appuser

# No command needed, container is used for data volume mounting
CMD ["tail", "-f", "/dev/null"]