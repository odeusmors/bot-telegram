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

flood_limit = 5
flood_interval = 10
user_messages = defaultdict(list)
blocked_words = ["hack gratuito", "senha123", "porn", "crack", "spam"]
warnings = defaultdict(int)

# ================= MONITORAMENTO RENDER =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, format, *args): return

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ================= BANCO DE DADOS =================
db_path = os.path.join(os.path.dirname(__file__), 'logs.db')
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, user TEXT, action TEXT)")
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

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "🛡️ *Comandos de Moderação:*\n"
        "/clear <n> - Limpa mensagens (incluindo ADMs)\n"
        "/fechar - Apenas ADMs podem falar\n"
        "/abrir - Libera o grupo para todos\n\n"
        "📌 *Geral:*\n"
        "/regras - Mostra as regras do grupo"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

async def regras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 *Regras:* Proibido flood, ofensas e links não autorizados.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_status = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if user_status.status not in ['administrator', 'creator']:
        return await update.message.reply_text("❌ Apenas administradores podem usar este comando.")

    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Use: /clear <quantidade>")

    quantidade = int(context.args[0])
    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    
    await update.message.delete() # Deleta o comando /clear

    apagadas = 0
    # Aumentamos o range de tentativas para garantir que pule IDs vazios
    for i in range(1, quantidade + 50):
        if apagadas >= quantidade: break
        try:
            await context.bot.delete_message(chat_id, message_id - i)
            apagadas += 1
        except Exception:
            continue

    aviso = await context.bot.send_message(chat_id, f"🧹 {apagadas} mensagens removidas do histórico.")
    await asyncio.sleep(3)
    await aviso.delete()

async def fechar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_status = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if user_status.status not in ['administrator', 'creator']: return
    
    await context.bot.set_chat_permissions(update.effective_chat.id, ChatPermissions(can_send_messages=False))
    await update.message.reply_text("🔒 *Grupo fechado!* Apenas administradores podem enviar mensagens.", parse_mode="Markdown")

async def abrir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_status = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if user_status.status not in ['administrator', 'creator']: return

    perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
    await context.bot.set_chat_permissions(update.effective_chat.id, perms)
    await update.message.reply_text("🔓 *Grupo aberto!* Todos podem enviar mensagens agora.", parse_mode="Markdown")

# ================= MODERAÇÃO AUTOMÁTICA =================

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.lower()
    
    if any(link in text for link in ["http", "t.me/"]):
        await update.message.delete()
        return

# ================= MAIN =================

async def main():
    if not TOKEN: return
    threading.Thread(target=run_health_check, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("regras", regras))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("fechar", fechar))
    app.add_handler(CommandHandler("abrir", abrir))
    
    # Filtro de texto
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        print("🚀 Bot rodando com sucesso!")
        while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())