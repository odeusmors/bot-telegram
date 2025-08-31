from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram.ext import filters
from telegram import Update, ChatPermissions
from collections import defaultdict
from flask import Flask
from threading import Thread
import re
import time
import datetime

# =============== CONFIGURAÇÕES ===============
TOKEN = "7607196071:AAG8r_6qfR_fOv-htcEVnNHoMcy1tnmHeZ4"

flood_limit = 5
flood_interval = 10
user_messages = defaultdict(list)
blocked_words = ["hack gratuito", "senha123", "porn", "crack", "spam"]
welcome_message = "👋 Bem-vindo(a), {user}! Respeite as regras e aproveite o grupo 🚀"
rules_text = """
📌 REGRAS DO GRUPO:
1. Respeito acima de tudo.
2. Proibido spam, links suspeitos e flood.
3. Evite mensagens só em CAPS.
4. Nada de palavras ofensivas/proibidas.
5. Contribua com conteúdo relevante 🙌
"""
warnings = defaultdict(int)
LOG_FILE = "logs.txt"

# =============== FUNÇÃO DE LOG (BRT) ===============
def log_event(event):
    timestamp = datetime.datetime.utcnow() + datetime.timedelta(hours=-3)  # UTC-3
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp_str}] {event}\n")
    print(f"[{timestamp_str}] {event}")

# =============== FLASK PARA MANTER ONLINE ===============
app = Flask('')

@app.route('/')
def home():
    return "Bot online!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()

# =============== COMANDOS BÁSICOS ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot de moderação ativo! Use /regras para ver as regras.")
    log_event(
        f"Comando /start usado por {update.message.from_user.username or update.message.from_user.first_name}"
    )

async def regras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(rules_text)
    log_event(
        f"Comando /regras usado por {update.message.from_user.username or update.message.from_user.first_name}"
    )

# =============== AJUDA INTERATIVA ===============
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 *Central de Comandos do Bot*

✨ *Moderação automática:*
🔗 Bloqueia links suspeitos  
🆙 Bloqueia mensagens só em CAPS  
❌ Bloqueia palavras proibidas  
⚡ Protege contra flood (muitas mensagens em sequência)  

🛡️ *Comandos de admin* (responda à mensagem do usuário):
⚠️ /warn → Dá um aviso ao usuário (3 avisos = ban automático)  
🔇 /mute → Silencia o usuário  
🔊 /unmute → Remove silêncio do usuário  
⛔ /ban → Bane o usuário  

📌 *Informações do grupo:*
📖 /regras → Mostra as regras do grupo  
💡 *Dica:* Respeite sempre as regras e colabore com conteúdo relevante!  

📬 *Observação:* Este bot mantém o grupo organizado e seguro automaticamente.
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")
    log_event(
        f"Comando /ajuda usado por {update.message.from_user.username or update.message.from_user.first_name}"
    )

# =============== BOAS-VINDAS ===============
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            welcome_message.format(user=member.first_name))
        log_event(
            f"Novo membro {member.username or member.first_name} entrou no grupo"
        )

# =============== MODERAÇÃO AUTOMÁTICA ===============
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text or ""

    # Bloquear links
    if "http://" in text or "https://" in text or "t.me/" in text:
        await update.message.delete()
        await context.bot.send_message(
            update.effective_chat.id,
            f"⛔ @{username}, links não são permitidos.")
        log_event(f"Link bloqueado de {username}: {text}")
        return

    # Bloquear capslock
    if text.isupper() and len(text) > 5:
        await update.message.delete()
        await context.bot.send_message(
            update.effective_chat.id,
            f"⚠️ @{username}, evite usar só MAIÚSCULAS.")
        log_event(f"Mensagem em CAPS bloqueada de {username}: {text}")
        return

    # Palavras proibidas
    for word in blocked_words:
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            await update.message.delete()
            await context.bot.send_message(
                update.effective_chat.id,
                f"🚫 @{username}, essa palavra não é permitida.")
            log_event(f"Palavra proibida bloqueada de {username}: {text}")
            return

    # Anti-flood
    now = time.time()
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < flood_interval]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > flood_limit:
        await update.message.delete()
        await context.bot.send_message(update.effective_chat.id,
                                       f"⚠️ @{username}, pare de floodar.")
        log_event(f"Flood detectado de {username}")
        return

# =============== RESPOSTAS AUTOMÁTICAS ===============
async def respostas_automaticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    username = update.message.from_user.username or update.message.from_user.first_name
    if "oi" in text or "olá" in text:
        await update.message.reply_text(f"Olá @{username}! 👋")
        log_event(f"Resposta automática 'Olá' enviada para {username}")
    elif "ajuda" in text:
        await update.message.reply_text(
            "Use o comando /ajuda para ver todos os comandos do bot.")
        log_event(f"Resposta automática 'ajuda' enviada para {username}")

# =============== COMANDOS DE ADMIN ===============
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❗ Use /warn respondendo a uma mensagem do usuário.")
        return
    user = update.message.reply_to_message.from_user
    warnings[user.id] += 1
    await update.message.reply_text(
        f"⚠️ @{user.username or user.first_name} recebeu um aviso ({warnings[user.id]}/3)."
    )
    log_event(
        f"{update.message.from_user.username} deu /warn em {user.username or user.first_name} ({warnings[user.id]}/3)"
    )
    if warnings[user.id] >= 3:
        await update.message.chat.kick_member(user.id)
        log_event(
            f"{user.username or user.first_name} foi banido após 3 avisos")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❗ Use /mute respondendo a uma mensagem do usuário.")
        return
    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=False)
    await context.bot.restrict_chat_member(update.effective_chat.id,
                                           user.id,
                                           permissions=permissions)
    log_event(
        f"{user.username or user.first_name} foi silenciado por {update.message.from_user.username}"
    )

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❗ Use /unmute respondendo a uma mensagem do usuário.")
        return
    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=True,
                                  can_send_media_messages=True)
    await context.bot.restrict_chat_member(update.effective_chat.id,
                                           user.id,
                                           permissions=permissions)
    log_event(
        f"{user.username or user.first_name} teve o silêncio removido por {update.message.from_user.username}"
    )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❗ Use /ban respondendo a uma mensagem do usuário.")
        return
    user = update.message.reply_to_message.from_user
    await update.message.chat.kick_member(user.id)
    log_event(
        f"{user.username or user.first_name} foi banido por {update.message.from_user.username}"
    )

# =============== MAIN ===============
def main():
    app_bot = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("regras", regras))
    app_bot.add_handler(CommandHandler("ajuda", ajuda))
    app_bot.add_handler(CommandHandler("warn", warn))
    app_bot.add_handler(CommandHandler("mute", mute))
    app_bot.add_handler(CommandHandler("unmute", unmute))
    app_bot.add_handler(CommandHandler("ban", ban))

    # Eventos
    app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), respostas_automaticas))

    print("✅ Bot rodando...")
    log_event("Bot iniciado e pronto para operação")

    # Loop seguro para reinício automático
    try:
        app_bot.run_polling()
    except Exception as e:
        log_event(f"⚠️ Bot caiu com erro: {e}. Reiniciando em 5 segundos...")
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()
