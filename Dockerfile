# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ключ в контейнер
COPY app/gothic-agility-464209-f4-39095fb8e054copy.json app/gothic-agility-464209-f4-39095fb8e054copy.json

# Copy the rest of the application's code into the container
COPY . .

# (Optional) Expose the port (Cloud Run ignores this, но не мешает)
EXPOSE 8000

# Run run_agent.py when the container launches
CMD ["python", "run_agent.py"] 