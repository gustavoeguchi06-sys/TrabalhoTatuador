#!/usr/bin/env bash
# Script de build executado pelo Render antes de subir o serviço.
# Encerra na primeira falha para o deploy não seguir com um passo quebrado.
set -o errexit

pip install -r requirements.txt

# Coleta os arquivos estáticos para o WhiteNoise servir em produção.
python manage.py collectstatic --no-input

# Aplica as migrações do banco.
python manage.py migrate
