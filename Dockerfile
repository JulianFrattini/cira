FROM andib/cira-dev

WORKDIR /cira

# Install missing Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./src ./src
COPY ./app.py ./app.py

CMD ["python", "app.py"]