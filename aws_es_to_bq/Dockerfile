# Stage 1: Base image
FROM python:3.9-slim as base

# Install Apache Beam SDK and other dependencies
RUN pip install --no-cache-dir \
    apache-beam[gcp]==2.54.0 \
    elasticsearch==7.17.9

# Copy files from the official SDK image, including script/dependencies
COPY --from=apache/beam_python3.9_sdk:2.54.0 /opt/apache/beam /opt/apache/beam

# Set the entrypoint to Apache Beam SDK launcher
ENTRYPOINT ["/opt/apache/beam/boot"]