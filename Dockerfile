# Python ka base image
FROM python:3.10-slim

# Tesseract OCR engine install karne ka command
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng

# Working directory set karein
WORKDIR /app

# Requirements copy karke libraries install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saara code copy karein
COPY . .

# Bot ko start karne ka command
CMD ["python", "main.py"]
