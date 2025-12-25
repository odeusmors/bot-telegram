import os
import re
import time
import datetime
import sqlite3
import asyncio
import threading
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer

# Bibliotecas do Telegram e Segurança
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from telegram import Update, ChatPermissions

# ================= CONFIGURAÇÃO DE AMBIENTE =================
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configurações do Bot
flood_limit = 5
flood_interval = 10
user_messages = defaultdict(list)
blocked_words = ["hack gratuito", "senha123", "porn", "crack", "spam"]
welcome_message = "👋 Bem-vindo(a), {user}! Respeite as regras e aproveite o grupo 🚀"
warnings = defaultdict(int)

# ================= SERVIDOR PARA O RENDER (HEALTH CHECK) =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, format, *args):
        return # Silencia os logs do servidor web no console

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Servidor de monitoramento iniciado na porta {port}")
    server.serve_forever()

# ================= BANCO DE DADOS =================
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

# ================= COMANDOS DE MODERAÇÃO =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de moderação ativo! Use /ajuda para ver os comandos.")
    log_event("Comando /start usado", user=update.effective_user.username)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificação de Admin
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if member.status not in ['administrator', 'creator']:
        await update.message.reply_text("❌ Apenas administradores podem limpar o chat.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use: /clear <quantidade>")
        return

    quantidade = int(context.args[0])
    chat_id = update.effective_chat.id
    
    # Apaga a mensagem do comando
    await update.message.delete()

    apagadas = 0
    msg_id = update.message.message_id

    # Tenta apagar as mensagens anteriores
    for i in range(min(quantidade, 100)):
        try:
            await context.bot.delete_message(chat_id, msg_id - (i + 1))
            apagadas += 1
        except Exception:
            continue

    confirmacao = await context.bot.send_message(chat_id, f"🧹 {apagadas} mensagens removidas!")
    await asyncio.sleep(3)
    await confirmacao.delete()
    log_event(f"Clear executado: {apagadas} msgs", user=update.effective_user.username)

# ================= MODERAÇÃO AUTOMÁTICA =================

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text

    # Bloquear links
    if any(link in text.lower() for link in ["http://", "https://", "t.me/"]):
        await update.message.delete()
        log_event(f"Link bloqueado", user=username)
        return

    # Anti-flood
    now = time.time()
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < flood_interval]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > flood_limit:
        await update.message.delete()
        log_event("Flood detectado", user=username)
        return

# ================= MAIN =================

async def main():
    if not TOKEN:
        print("ERRO: TELEGRAM_TOKEN não configurado!")
        return

    # Inicia o servidor web para o Render não derrubar o bot
    threading.Thread(target=run_health_check, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers de comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    
    # Handlers de mensagens (Boas-vindas e Filtros)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))

    print("🚀 Bot iniciado e monitorando...")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass