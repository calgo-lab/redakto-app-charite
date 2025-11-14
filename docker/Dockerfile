FROM python:3.12

WORKDIR /app

RUN pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128 && rm -rf /root/.cache/pip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

RUN mkdir -p \
    flair_cache_root \
	models
    
COPY flair_cache_root/ /app/flair_cache_root/

COPY models/ /app/models/

COPY app.py streamlit_app.py favicon.ico logo.png calgo_lab_logo.png ./

COPY configs/ /app/configs/

COPY src/ /app/src/

ENV TOKENIZERS_PARALLELISM=false

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000"]