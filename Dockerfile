# Imagem enxuta do Python
FROM python:3.12-slim

WORKDIR /app

# Instala as dependências primeiro (aproveita o cache de camadas do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Executa o pipeline completo: ETL -> análise -> dashboard
CMD ["sh", "-c", "python etl.py && python analise.py && python dashboard.py"]
