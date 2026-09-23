# Official AWS Lambda Python 3.11 Base Image
FROM public.ecr.aws/lambda/python:3.11

# Set working directory inside container
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy dependency requirements
COPY requirements.txt .

# Install dependencies into AWS Lambda task root
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy application module code and handler
COPY vectorizer_module.py .
COPY handler.py .

# Set the AWS Lambda handler entrypoint function
CMD [ "handler.lambda_handler" ]
