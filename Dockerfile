FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Print directory content before copying files
RUN ls -la /app

# Copy project files
COPY . /app

# Print directory content after copying files
RUN ls -la /app

# Install dependencies
RUN pip install --no-cache-dir flask pyyaml gunicorn

# Expose port if needed (uncomment if the bot runs a server)
# EXPOSE 8000

# Run the bot
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]