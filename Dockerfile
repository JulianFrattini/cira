FROM cira-dev

COPY ./src/ ./src/
COPY ./test/ ./test/
COPY ./pytest.ini .
COPY ./conftest.py .
COPY ./demonstration.ipynb .
