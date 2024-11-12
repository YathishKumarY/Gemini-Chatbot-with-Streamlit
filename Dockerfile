FROM python:3.9.20

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD [ "streamlit", "run", "main.py" ]
