# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Command to run the app
CMD ["python", "src/dashboard/build_dashboard.py"]