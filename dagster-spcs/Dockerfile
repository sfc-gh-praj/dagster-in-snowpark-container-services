FROM python:3.10-slim

# Set environment variables
ENV DAGSTER_HOME=/opt/dagster/dagster_home
ENV PYTHONPATH=/opt/dagster/app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/dagster/dagster_home /opt/dagster/app

WORKDIR /opt/dagster/app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy dagster instance YAML to $DAGSTER_HOME
COPY dagster.yaml /opt/dagster/dagster_home/

# Copy your code and workspace to /opt/dagster/app
COPY workspace.yaml /opt/dagster/app/

# Copy source code

COPY dagster_project ./dagster_project

#COPY .env /opt/dagster/app/

# Make script executable
COPY startdagster.sh /opt/dagster/app/
RUN chmod +x /opt/dagster/app/startdagster.sh

EXPOSE 3000

# Start Dagster Webserver and Deamon process
CMD ["/opt/dagster/app/startdagster.sh"]
# CMD ["dagster-webserver","-w", "workspace.yaml", "-h", "0.0.0.0", "-p", "3000"]