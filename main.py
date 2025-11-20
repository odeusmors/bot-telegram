from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram.ext import filters
from telegram import Update, ChatPermissions
from collections import defaultdict
import re
import time
import datetime
import sqlite3

# ================= CONFIGURAÇÕES =================
TOKEN = "7607196071:AAGLTY4LdKS3IsAu97Ufy8thkX6Hm34c7fU"

flood_limit = 5
flood_interval = 10
user_messages = defaultdict(list)
blocked_words = ["hack gratuito", "senha123", "porn", "crack", "spam"]
welcome_message = "👋 Bem-vindo(a), {user}! Respeite as regras e aproveite o grupo 🚀"

# ================= BANCO DE DADOS =================
conn = sqlite3.connect('logs.db', check_same_thread=False)
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

# ================= FUNÇÃO DE LOG =================
def log_event(event, user=None):
    timestamp = datetime.datetime.utcnow() + datetime.timedelta(hours=-3)
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO logs (timestamp, user, action) VALUES (?, ?, ?)",
        (timestamp_str, user, event)
    )
    conn.commit()

    print(f"[{timestamp_str}] {event}")

# ================= COMANDO START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot de moderação ativo! Use /regras para ver as regras."
    )
    log_event("Comando /start usado", user=update.message.from_user.username)

# ================= AJUDA =================
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
🧹 /clear <n> → Apaga as últimas n mensagens  

📌 *Informações do grupo:*
📖 /regras → Mostra as regras do grupo  
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")
    log_event("Comando /ajuda usado", user=update.message.from_user.username)

# ================= REGRAS =================
async def regras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_text = """
📌 *Regras do Grupo*

1️⃣ Respeito acima de tudo.  
2️⃣ Proibido spam, links suspeitos e flood.  
3️⃣ Evite mensagens só em CAPS.  
4️⃣ Nada de palavras ofensivas/proibidas.  
5️⃣ Contribua com conteúdo relevante 🙌  
"""
    await update.message.reply_text(rules_text, parse_mode="Markdown")
    log_event("Comando /regras usado", user=update.message.from_user.username)

# ================= BOAS-VINDAS =================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(welcome_message.format(user=member.first_name))
        log_event(f"Novo membro entrou: {member.username or member.first_name}")

# ================= MODERAÇÃO AUTOMÁTICA =================
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text or ""

    # Bloquear links
    if "http://" in text or "https://" in text or "t.me/" in text:
        await update.message.delete()
        await context.bot.send_message(
            update.effective_chat.id,
            f"⛔ @{username}, links não são permitidos."
        )
        log_event(f"Link bloqueado: {text}", user=username)
        return

    # CAPSLOCK
    if text.isupper() and len(text) > 5:
        await update.message.delete()
        await context.bot.send_message(
            update.effective_chat.id,
            f"⚠️ @{username}, evite usar só MAIÚSCULAS."
        )
        log_event(f"Mensagem em CAPS bloqueada: {text}", user=username)
        return

    # Palavras proibidas
    for word in blocked_words:
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            await update.message.delete()
            await context.bot.send_message(
                update.effective_chat.id,
                f"🚫 @{username}, essa palavra não é permitida."
            )
            log_event(f"Palavra proibida: {text}", user=username)
            return

    # Anti-flood
    now = time.time()
    user_messages[user_id] = [
        t for t in user_messages[user_id] if now - t < flood_interval
    ]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > flood_limit:
        await update.message.delete()
        await context.bot.send_message(
            update.effective_chat.id,
            f"⚠️ @{username}, pare de floodar."
        )
        log_event("Flood detectado", user=username)
        return

# ================= RESPOSTAS AUTOMÁTICAS =================
async def respostas_automaticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    username = update.message.from_user.username or update.message.from_user.first_name

    if "oi" in text or "olá" in text:
        await update.message.reply_text(f"Olá @{username}! 👋")
        log_event("Resposta automática 'olá' enviada", user=username)

    elif "ajuda" in text:
        await update.message.reply_text("Use o comando /ajuda para ver todos os comandos do bot.")
        log_event("Resposta automática 'ajuda' enviada", user=username)

# ================= SISTEMA DE AVISOS =================
from collections import defaultdict
warnings = defaultdict(int)

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /warn respondendo à mensagem do usuário.")
        return

    user = update.message.reply_to_message.from_user
    warnings[user.id] += 1

    await update.message.reply_text(
        f"⚠️ @{user.username or user.first_name} recebeu um aviso ({warnings[user.id]}/3)."
    )
    log_event(f"Aviso aplicado em {user.username}", user=update.message.from_user.username)

    if warnings[user.id] >= 3:
        await update.message.chat.kick_member(user.id)
        log_event(f"Usuário banido após 3 avisos: {user.username}")

# ================= COMANDO MUTE =================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /mute respondendo a uma mensagem.")
        return

    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=False)

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        permissions=permissions
    )
    log_event(f"Usuário silenciado: {user.username}")

# ================= COMANDO UNMUTE =================
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /unmute respondendo a uma mensagem.")
        return

    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True
    )

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        permissions=permissions
    )
    log_event(f"Silêncio removido de: {user.username}")

# ================= COMANDO BAN =================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /ban respondendo a uma mensagem.")
        return

    user = update.message.reply_to_message.from_user
    await update.message.chat.kick_member(user.id)
    log_event(f"Usuário banido: {user.username}")

# ================= COMANDO CLEAR =================
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0 or not context.args[0].isdigit():
        await update.message.reply_text("Use: /clear <quantidade>\nEx: /clear 5")
        return

    quantidade = int(context.args[0])
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id
    apagadas = 0

    for i in range(quantidade + 1):
        try:
            await context.bot.delete_message(chat_id, msg_id - i)
            apagadas += 1
        except:
            pass

    log_event(
        f"{apagadas} mensagens apagadas pelo /clear",
        user=update.message.from_user.username
    )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("regras", regras))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("clear", clear))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), respostas_automaticas))

    print("Bot rodando...")
    log_event("Bot iniciado com sucesso")

    app.run_polling()

if __name__ == "__main__":
    main()
