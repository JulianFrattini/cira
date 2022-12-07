FROM ghcr.io/julianfrattini/cira-dev:latest

WORKDIR /cira

# Install Python dependencies and setup cira version
COPY setup.py .
RUN pip3 install -e .

COPY ./src ./src
COPY ./app.py ./app.py

CMD ["python", "app.py"]