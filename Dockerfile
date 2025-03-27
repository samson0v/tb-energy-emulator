FROM python:3.11-slim AS build

# Copy the application code and configuration
ADD . /

# Set environment variables
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=.

EXPOSE 5040 5041 5042 5043 5044 5045 5046

# Install Python packages
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the remaining files
COPY . .

# Set the container command
CMD [ "python3", "./tb_energy_emulator/energy_emulator.py" ]