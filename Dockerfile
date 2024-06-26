FROM python:3-slim
WORKDIR /programas/api-students
# Instalar las dependencias necesarias
RUN pip3 install flask flask-restx
COPY . .
RUN python3 db.py
CMD ["python3", "./app-swagger.py"]
