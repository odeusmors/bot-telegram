# 🤖 Bot de Moderação para Telegram

Este projeto é um **bot de moderação** para grupos do Telegram, com funcionalidades automáticas e comandos de administração. Ele foi desenvolvido em **Python** e está hospedado no **Render.com** para funcionar 24/7, com **logs persistentes** em SQLite.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.11+**
- **[python-telegram-bot](https://python-telegram-bot.org/)** >= 20.0
- **Flask** – para manter o bot online com web server
- **SQLite3** – banco de dados para logs persistentes
- **Render.com** – hospedagem e deploy contínuo via GitHub




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

