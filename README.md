# Controle Financeiro — Tatuador
## Visão geral

Este projeto fornece uma aplicação web simples para registrar serviços de tatuagem e acompanhar as finanças (receitas, custos e lucro). A implementação atual usa Django para renderizar o front-end no servidor e SQLite para armazenamento local.

Principais componentes
- Backend: Django app `finance` (modelo `Transaction`, views, URLs e admin).
- Front-end: template server-rendered em `templates/finance/front.html` e estilos em `static/css/visual.css`.

## Funcionalidades implementadas

- Registrar serviços (cliente, data, descrição, preço, custo, forma de pagamento, observações).
- Listar transações com filtros por período e cliente.
- Resumo financeiro (receita total, despesas, lucro) calculado no servidor.
- Interface administrativa via Django Admin (`/admin`).

## Requisitos

- Python 3.10+ (recomendado).
- pip (gerenciador de pacotes).
- Sistema operacional: Windows (instruções fornecidas), outras plataformas também suportadas.

## Instalação (Windows - PowerShell)

1. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
```

2. Ative o ambiente (duas opções):

- Opção A — Ativar com política temporária (recomendada):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
```

- Opção B — Sem alterar política (executar comandos diretamente com o Python do venv):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver
```

3. Instale dependências:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

4. Aplique migrações e crie o banco de dados:

```powershell
.venv\Scripts\python.exe manage.py migrate
```

5. (Opcional) Crie um superusuário para acessar o admin:

```powershell
.venv\Scripts\python.exe manage.py createsuperuser
```

6. Inicie o servidor de desenvolvimento:

```powershell
.venv\Scripts\python.exe manage.py runserver 8000
```

7. Abra o navegador em: http://127.0.0.1:8000/

## Estrutura do projeto

- `manage.py` — utilitário de linha de comando do Django.
- `tattoo_finance/` — configurações do projeto (settings, urls, wsgi).
- `finance/` — app principal com modelos, views, URLs e admin.
- `templates/finance/front.html` — template do front-end.
- `static/css/visual.css` — estilos.
- `requirements.txt` — dependências (Django).

## Como funciona o front-end

O formulário em `templates/finance/front.html` envia requisições POST ao servidor para criar transações. A listagem e os filtros são processados em `finance/views.py` e a página é renderizada no servidor (sem JavaScript obrigatório). Se preferir um front com JavaScript, posso adicionar endpoints REST para que a interface cliente consuma JSON.

## Banco de dados

- Por padrão o projeto usa SQLite (`db.sqlite3`). Para utilizar outro banco (Postgres, MySQL), atualize `tattoo_finance/settings.py` em `DATABASES`.

### Usando MySQL

O projeto suporta MySQL lendo variáveis de ambiente. Se você preferir MySQL, siga os passos abaixo:

1. Instale o servidor MySQL (ou MariaDB) no seu sistema e crie um banco e um usuário:

```sql
CREATE DATABASE tattoo_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'tattoo'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON tattoo_finance.* TO 'tattoo'@'localhost';
FLUSH PRIVILEGES;
```

2. Defina as variáveis de ambiente (temporariamente na sessão PowerShell):

```powershell
$env:MYSQL_DATABASE='tattoo_finance'
$env:MYSQL_USER='tattoo'
$env:MYSQL_PASSWORD='sua_senha_segura'
$env:MYSQL_HOST='127.0.0.1'
$env:MYSQL_PORT='3306'
```

Se preferir persistir as variáveis, use `setx` (reabra o terminal depois).

3. Instale dependências e rode as migrations (PyMySQL já está no `requirements.txt`):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver
```

Observações:
- O `tattoo_finance/settings.py` detecta a presença da variável `MYSQL_DATABASE` e, se encontrada, configura Django para usar MySQL; caso contrário, permanece em SQLite.
- No Windows a instalação de `mysqlclient` (biblioteca nativa) pode requerer dependências C; por isso o projeto usa `PyMySQL` (pure-Python) para compatibilidade mais fácil. Se preferir `mysqlclient`, instale-o e ajuste `requirements.txt`.

## Testes manuais e validação

- Execute o servidor e acesse a página principal; crie algumas transações para validar cálculos de receita/custo/lucro.
- Verifique o admin em `/admin` (após criar superusuário) para inspeção direta dos registros.

## Próximos passos recomendados

- Adicionar API REST (Django REST Framework) para suportar front-end JavaScript e integrações móveis.
- Exportar/importar CSV para backup e transferências de dados.
- Adicionar autenticação multi-usuário para que cada tatuador gerencie suas próprias transações.
- Relatórios por período (mensal, anual) e gráficos para análise visual.

## Suporte e contribuições

- Para bugs ou melhorias, abra uma issue descrevendo o problema e passos para reproduzir.
- Se quiser, eu posso implementar endpoints REST, export CSV ou adicionar autenticação.

---

Arquivo atualizado para apresentar instruções e contexto de forma profissional.
