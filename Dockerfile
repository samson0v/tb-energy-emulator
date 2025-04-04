FROM python:3.11-slim AS build

ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Copy the application code and configuration
ADD . /

# Set environment variables
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"
ENV PYTHONPATH=.

EXPOSE 5040 5041 5042 5043 5044 5045 5046

# Install Python packages
COPY requirements.txt .
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends \
    gcc python3-dev build-essential libssl-dev libffi-dev zlib1g-dev \
    python3-grpcio curl pkg-config libssl-dev &&  \
    case "$TARGETPLATFORM" in \
        "linux/amd64") DEFAULT_HOST="x86_64-unknown-linux-gnu";; \
        "linux/386") DEFAULT_HOST="i686-unknown-linux-gnu";; \
        "linux/arm64") DEFAULT_HOST="aarch64-unknown-linux-gnu";; \
        "linux/arm/v7") DEFAULT_HOST="armv7-unknown-linux-gnueabihf";; \
        *) \
            echo "Unsupported platform detected. Trying to use default value...";; \
        esac && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y --default-host=$DEFAULT_HOST --profile minimal && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* && \
    rustup self uninstall -y && \
    apt-get remove --purge -y gcc python3-dev build-essential libssl-dev libffi-dev zlib1g-dev pkg-config && \
    apt-get autoremove -y

# Copy the remaining files
COPY . .

# Set the container command
CMD [ "python3", "./tb_energy_emulator/energy_emulator.py" ]