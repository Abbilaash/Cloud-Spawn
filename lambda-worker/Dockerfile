# Official AWS Lambda Python 3.11 Base Image
FROM public.ecr.aws/lambda/python:3.11

# Set working directory inside container (read about manifest error[multi and single])
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy dependency requirements
COPY requirements.txt .

# Upgrade pip to ensure support for modern manylinux wheel tags
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies strictly using pre-compiled binary wheels into AWS Lambda task root
RUN pip install --no-cache-dir --only-binary :all: --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application module code and handler
COPY vectorizer_module.py .
COPY handler.py .

# Set the AWS Lambda handler entrypoint function
CMD [ "handler.lambda_handler" ]
