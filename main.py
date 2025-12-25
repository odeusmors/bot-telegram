import os
import re
import time
import datetime
import sqlite3
import asyncio
from collections import defaultdict
from dotenv import load_dotenv 

from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from telegram import Update, ChatPermissions

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ================= CONFIGURAÇÕES =================
flood_limit = 5
flood_interval = 10
user_messages = defaultdict(list)
blocked_words = ["hack gratuito", "senha123", "porn", "crack", "spam"]
welcome_message = "👋 Bem-vindo(a), {user}! Respeite as regras e aproveite o grupo 🚀"

# ================= BANCO DE DADOS =================
# Usamos caminhos absolutos para evitar erros no Render
db_path = os.path.join(os.path.dirname(__file__), 'logs.db')
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user TEXT,
    action TEXT
)
""")
conn.commit()

def log_event(event, user=None):
    timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (timestamp, user, action) VALUES (?, ?, ?)", (timestamp_str, user, event))
    conn.commit()
    print(f"[{timestamp_str}] {event}")

# ================= COMANDOS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de moderação ativo!")
    log_event("Comando /start usado", user=update.effective_user.username)

# CORREÇÃO DO CLEAR
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificar se o usuário é admin antes de apagar
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if member.status not in ['administrator', 'creator']:
        await update.message.reply_text("❌ Apenas administradores podem usar este comando.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use: /clear <quantidade>")
        return

    quantidade = int(context.args[0])
    chat_id = update.effective_chat.id
    
    # Apaga a mensagem do comando /clear primeiro
    await update.message.delete()

    apagadas = 0
    msg_id = update.message.message_id

    # Tentativa de apagar mensagens anteriores (limite de 100 para evitar travamentos)
    for i in range(min(quantidade, 100)):
        try:
            await context.bot.delete_message(chat_id, msg_id - (i + 1))
            apagadas += 1
        except Exception:
            continue # Ignora mensagens que não podem ser apagadas

    confirmacao = await context.bot.send_message(chat_id, f"🧹 {apagadas} mensagens limpas!")
    # Auto-deleta a mensagem de confirmação após 3 segundos
    await asyncio.sleep(3)
    await confirmacao.delete()

# ... (outras funções mantidas, mas recomendo unificar MessageHandlers)

# ================= MAIN =================
async def main():
    if not TOKEN:
        print("ERRO: Token não encontrado! Verifique o arquivo .env ou variáveis de ambiente.")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    await app.bot.delete_webhook(drop_pending_updates=True)

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    # Adicione os outros handlers aqui...

    # Handler de moderação (deve ser um dos últimos para não interceptar tudo antes)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))

    print("Bot rodando...")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass