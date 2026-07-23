# Controle Financeiro & Agenda — Tatuador
## Visão geral

Este projeto fornece uma aplicação web para registrar serviços de tatuagem, acompanhar as finanças (receitas, custos e lucro) e gerenciar a agenda de sessões com lembretes por notificação push do navegador. A implementação usa Django para renderizar o front-end no servidor e SQLite para armazenamento local.

Principais componentes
- Backend: Django app `finance` (modelos `Transaction`, `Appointment`, `PushSubscription`, views, URLs e admin).
- Front-end: templates server-rendered em `templates/finance/` e estilos em `static/css/visual.css`.
- Notificações: Web Push (pywebpush + VAPID) com service worker e verificador de lembretes em background.

## Funcionalidades implementadas

- Registrar serviços (cliente, data, descrição, preço, custo, forma de pagamento, observações).
- Listar transações com filtros por período e cliente.
- Resumo financeiro (receita total, despesas, lucro) calculado no servidor.
- Agenda de tatuagens (`/agenda/`): agendar sessões com cliente, telefone, data, horário, duração e valor estimado; concluir, cancelar ou excluir; histórico de sessões.
- Ao concluir uma sessão, o formulário do financeiro abre pré-preenchido com cliente, valor e descrição.
- Notificações push do navegador com três lembretes automáticos:
  - 🔔 Resumo do dia a partir das 08:00 — "Hoje você tem N atendimentos."
  - 🔔 1 hora antes — "Você tem uma tatuagem às 14:00."
  - 🔔 30 minutos antes — "Sua próxima sessão é em 30 minutos."
- Interface administrativa via Django Admin (`/admin`).

## Como ativar as notificações

1. Inicie o servidor e abra o sistema no navegador (Chrome, Edge ou Firefox).
2. Clique em **"Ativar lembretes"** (sino no topo da página) e permita as notificações quando o navegador perguntar.
3. Pronto — uma notificação de confirmação é enviada na hora e os lembretes da agenda passam a chegar automaticamente enquanto o servidor estiver rodando.

Observações:
- As chaves VAPID são geradas automaticamente no primeiro uso e salvas em `vapid_private_key.pem` (não versionar).
- O verificador de lembretes roda em background junto com o servidor (checagem a cada 60 segundos, fuso `America/Sao_Paulo`).
- Notificações push exigem contexto seguro: funcionam em `http://localhost` / `127.0.0.1` ou via HTTPS em produção.

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

5. Crie um usuário para entrar no sistema (o app inteiro exige login):

```powershell
.venv\Scripts\python.exe manage.py createsuperuser
```

6. Inicie o servidor de desenvolvimento:

```powershell
.venv\Scripts\python.exe manage.py runserver 8000
```

7. Abra o navegador em: http://127.0.0.1:8000/ e entre com o usuário criado no passo 5.

## Autenticação

Todas as páginas e endpoints exigem login (`LoginRequiredMiddleware`); apenas `/sw.js` (service worker) e a própria tela de login são públicos. Crie usuários com `createsuperuser` ou pelo admin em `/admin`.

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste. As principais:

- `DJANGO_SECRET_KEY` — **obrigatória em produção**; sem ela o app não sobe (em desenvolvimento com `DJANGO_DEBUG=True` há um valor padrão inseguro).
- `DJANGO_DEBUG` — `True` local, `False` em produção (padrão no Render).
- `DATABASE_URL` — conexão do banco; **no Render é obrigatória** (sem ela o deploy falha em vez de cair no SQLite efêmero e perder dados). É injetada automaticamente ao vincular um Postgres do Render.
- `MYSQL_*` — alternativa ao `DATABASE_URL` para quem usa MySQL; se `DATABASE_URL` estiver definida, ela tem prioridade.
- `DJANGO_ALLOWED_HOSTS` — hosts extras (domínio personalizado), separados por vírgula; o domínio `*.onrender.com` é adicionado automaticamente.
- `VAPID_PRIVATE_KEY` — conteúdo do PEM da chave de push; necessária em produção para as inscrições sobreviverem aos deploys.

## Deploy no Render

O repositório já vem com um Blueprint (`render.yaml`) que provisiona o serviço web e um banco Postgres.

1. Faça push do projeto para um repositório no GitHub/GitLab.
2. No [dashboard do Render](https://dashboard.render.com/), clique em **New > Blueprint** e selecione o repositório. O Render lê o `render.yaml` e cria o Postgres e o serviço web.
3. Antes do primeiro deploy, defina a variável **`VAPID_PRIVATE_KEY`** no serviço web (Environment) com o conteúdo do seu `vapid_private_key.pem`. Sem ela, as inscrições de push são perdidas a cada deploy.
   - `DJANGO_SECRET_KEY` é gerada automaticamente pelo Render e `DATABASE_URL` é vinculada ao Postgres — não precisa preencher à mão.
4. O build roda `bash build.sh` (instala dependências, `collectstatic` e `migrate`); o serviço sobe com `gunicorn tattoo_finance.wsgi:application`.
5. Após o deploy, crie o usuário de acesso pelo Shell do serviço no Render:

   ```bash
   python manage.py createsuperuser
   ```

Observações:
- O disco do Render é efêmero: os dados ficam no Postgres, não em SQLite. O app falha no boot se `DATABASE_URL` não estiver presente em produção, justamente para evitar perda silenciosa de dados.
- No plano gratuito o serviço hiberna após inatividade; os lembretes em thread só rodam com o serviço ativo. Para lembretes confiáveis, use um Cron Job do Render chamando `python manage.py send_reminders`.

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

## Testes

```powershell
.venv\Scripts\python.exe manage.py test finance
```

Cobrem: parsing de valores em formato brasileiro, validação dos formulários, exigência de login, exclusão apenas via POST, totais financeiros e idempotência dos lembretes.

## Lembretes: thread ou cron

Por padrão o verificador roda numa thread dentro do processo web (checagem a cada 60 s). Alternativa mais robusta para produção: agendar `python manage.py send_reminders` num cron (ex: um Cron Job do Render a cada 5 minutos). O `NotificationLog` impede envios duplicados mesmo com os dois ativos.

## Próximos passos recomendados

- Adicionar API REST (Django REST Framework) para suportar front-end JavaScript e integrações móveis.
- Exportar/importar CSV para backup e transferências de dados.
- Relatórios por período (mensal, anual) e gráficos para análise visual.

## Suporte e contribuições

- Para bugs ou melhorias, abra uma issue descrevendo o problema e passos para reproduzir.
- Se quiser, eu posso implementar endpoints REST, export CSV ou adicionar autenticação.

---

Arquivo atualizado para apresentar instruções e contexto de forma profissional.
