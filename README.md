# 🤖 Bot de Moderação para Telegram

Este é um bot de moderação para grupos do Telegram, projetado para manter o grupo seguro e organizado automaticamente.

---

## 🔹 Funcionalidades

### Moderação Automática
- 🔗 Bloqueia links suspeitos
- 🆙 Bloqueia mensagens apenas em CAPS
- ❌ Bloqueia palavras proibidas
- ⚡ Proteção contra flood (muitas mensagens em sequência)

### Comandos de Admin
- ⚠️ `/warn` → Dá um aviso ao usuário (3 avisos = ban automático)  
- 🔇 `/mute` → Silencia o usuário  
- 🔊 `/unmute` → Remove silêncio do usuário  
- ⛔ `/ban` → Bane o usuário  

### Informações do Grupo
- 📖 `/regras` → Mostra as regras do grupo  
- 🤖 `/ajuda` → Exibe todos os comandos do bot  

---

## ⚙️ Configuração

1. Clone este repositório ou faça o download dos arquivos.
2. Instale as dependências:
   ```bash
   pip install python-telegram-bot flask watchdog

Adicione o TOKEN do bot fornecido pelo @BotFather
 no arquivo main.py.

Execute o bot:

python main.py

📝 Logs

O bot gera logs de todas as atividades e comandos em logs.txt com horário em BRT (UTC-3).

💡 Dicas

Sempre respeite os limites de mensagens do grupo para evitar acionamento da proteção contra flood.

Atualize a lista de palavras proibidas em main.py conforme a necessidade do grupo.

O bot funciona automaticamente ao iniciar, não sendo necessário reiniciar manualmente.

📌 Observações

Desenvolvido para grupos privados e públicos.

Futuras atualizações podem incluir novos comandos e funcionalidades avançadas de moderação.