FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install flask pyyaml gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
