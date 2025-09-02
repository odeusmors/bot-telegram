# 🤖 Bot de Moderação para Telegram

Este projeto é um **bot de moderação** para grupos do Telegram, com funcionalidades automáticas e comandos de administração. Ele foi desenvolvido em **Python** e está hospedado no **Render.com** para funcionar 24/7, com **logs persistentes** em SQLite.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.11+**
- **[python-telegram-bot](https://python-telegram-bot.org/)** >= 20.0
- **Flask** – para manter o bot online com web server
- **SQLite3** – banco de dados para logs persistentes
- **Render.com** – hospedagem e deploy contínuo via GitHub

---

## 📁 Estrutura do Projeto

bot-telegram/
│
├─ main.py # Código principal do bot
├─ consultar_logs.py # Script para consultar logs no SQLite
├─ requirements.txt # Dependências do projeto
├─ logs.db # Banco de dados SQLite (criado automaticamente)
└─ README.md # Documentação do projeto


---

🤖 Bot de Moderação para Telegram
Este é um bot de moderação para grupos do Telegram, projetado para manter o grupo seguro e organizado automaticamente.

🔹 Funcionalidades
Moderação Automática
🔗 Bloqueia links suspeitos
🆙 Bloqueia mensagens apenas em CAPS
❌ Bloqueia palavras proibidas
⚡ Proteção contra flood (muitas mensagens em sequência)
Comandos de Admin
⚠️ /warn → Dá um aviso ao usuário (3 avisos = ban automático)
🔇 /mute → Silencia o usuário
🔊 /unmute → Remove silêncio do usuário
⛔ /ban → Bane o usuário
Informações do Grupo
📖 /regras → Mostra as regras do grupo
🤖 /ajuda → Exibe todos os comandos do bot


## ⚙️ Funcionalidades

### Moderação Automática
- Bloqueio de links suspeitos (`http://`, `https://`, `t.me/`)  
- Bloqueio de mensagens somente em CAPS  
- Bloqueio de palavras proibidas (configuráveis em `blocked_words`)  
- Proteção contra flood (limite de mensagens por usuário)

### Comandos de Admin
- `/warn` → dá aviso ao usuário (3 avisos = ban automático)  
- `/mute` → silencia o usuário  
- `/unmute` → remove silêncio  
- `/ban` → bane o usuário  

### Boas-vindas Automáticas
- Mensagem de boas-vindas personalizada para novos membros

### Logs Persistentes
- Todas as ações do bot e do admin são registradas no **SQLite** (`logs.db`)  
- É possível consultar os logs com `consultar_logs.py`

---

## 🚀 Configuração e Execução

### 1. Configuração Local
1. Clone o projeto:
```bash
git clone https://github.com/odeusmors/bot-telegram
cd bot-telegram


Instale as dependências:

pip install -r requirements.txt


Substitua o token do bot no main.py:

TOKEN = "SEU_TOKEN_AQUI"


Execute o bot localmente:

python main.py

2. Deploy no Render

Crie um Web Service no Render.

Conecte ao repositório GitHub.

Configure:

Environment: Python 3

Build Command: pip install -r requirements.txt

Start Command: python main.py

Render fará deploy automático a cada commit na branch configurada.

⚡ O Render reinicia automaticamente o bot se houver quedas.

3. Consultar Logs

Use o script consultar_logs.py para visualizar histórico do bot:

python consultar_logs.py


Mostra todos os logs, ou filtre por usuário/ação alterando as linhas no final do script.

📝 Observações

O arquivo logs.db é criado automaticamente na primeira execução do bot.

Não execute mais de uma instância do bot ao mesmo tempo (pode causar erro de conflito getUpdates).

Para produção, recomenda-se usar webhook em vez de polling para evitar conflitos.

🔧 Dicas

Atualize o bot localmente → commit → push → Render faz deploy automático.

Monitore logs em tempo real pelo painel do Render ou via consultar_logs.py.

Configure blocked_words e mensagens personalizadas diretamente no main.py.