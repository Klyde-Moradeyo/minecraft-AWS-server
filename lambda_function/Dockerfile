# Use a base image that includes Python and necessary build tools
FROM amazonlinux:2

# Install required dependencies
RUN yum install -y \
    python3-pip \
    zip \
    gcc \
    libffi-devel \
    python3-devel \
    openssl-devel \
    dos2unix \
    unzip

# Set the working directory
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Install Python dependencies
RUN pip3 install -t package -r requirements.txt

# Set appropriate file permissions
RUN chmod 644 "lambda_function.py" "package"
RUN chmod 755 "lambda_function.py" "package"

# Copy lambda_function.py to the package directory
RUN cp -r lambda_function.py utils package/

# Create the lambda zip file
RUN (cd package && zip -r ../lambda_function_payload.zip .)

# Clean up the package directory
RUN rm -rf "package"