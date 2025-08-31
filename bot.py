from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram.ext import filters
from telegram import Update, ChatPermissions
from collections import defaultdict
import re
import time

# =============== CONFIGURAÇÕES ===============
TOKEN = "7607196071:AAG8r_6qfR_fOv-htcEVnNHoMcy1tnmHeZ4"  # coloque o token do BotFather

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

warnings = defaultdict(int)  # contador de avisos por usuário

# =============== FUNÇÕES BÁSICAS ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de moderação ativo! Use /regras para ver as regras.")

async def regras(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(rules_text)

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 *Comandos do Bot:*

📌 Moderação automática:
- Bloqueia links suspeitos
- Bloqueia CAPSLOCK
- Bloqueia palavras proibidas
- Bloqueia flood (muitas mensagens seguidas)

📌 Comandos de admin (responda a mensagem do usuário):
- /warn → Dá um aviso ao usuário (3 avisos = ban automático)
- /mute → Silencia o usuário
- /unmute → Remove silêncio do usuário
- /ban → Bane o usuário

📌 Informações do grupo:
- /regras → Mostra as regras do grupo
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(welcome_message.format(user=member.first_name))

# =============== MODERAÇÃO AUTOMÁTICA ===============
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text or ""

    # 1. Bloquear links
    if "http://" in text or "https://" in text or "t.me/" in text:
        await update.message.delete()
        await context.bot.send_message(update.effective_chat.id,
                                       f"⛔ @{username}, links não são permitidos.")
        return

    # 2. Bloquear capslock
    if text.isupper() and len(text) > 5:
        await update.message.delete()
        await context.bot.send_message(update.effective_chat.id,
                                       f"⚠️ @{username}, evite usar só MAIÚSCULAS.")
        return

    # 3. Palavras proibidas
    for word in blocked_words:
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            await update.message.delete()
            await context.bot.send_message(update.effective_chat.id,
                                           f"🚫 @{username}, essa palavra não é permitida.")
            return

    # 4. Anti-flood
    now = time.time()
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < flood_interval]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > flood_limit:
        await update.message.delete()
        await context.bot.send_message(update.effective_chat.id,
                                       f"⚠️ @{username}, pare de floodar.")
        return

# =============== RESPOSTAS AUTOMÁTICAS SIMPLES ===============
async def respostas_automaticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "oi" in text or "olá" in text:
        await update.message.reply_text(f"Olá @{update.message.from_user.first_name}! 👋")
    elif "ajuda" in text:
        await update.message.reply_text("Use o comando /ajuda para ver todos os comandos do bot.")

# =============== COMANDOS DE ADMIN ===============
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /warn respondendo a uma mensagem do usuário.")
        return

    user = update.message.reply_to_message.from_user
    warnings[user.id] += 1
    await update.message.reply_text(f"⚠️ @{user.username or user.first_name} recebeu um aviso ({warnings[user.id]}/3).")

    if warnings[user.id] >= 3:
        await update.message.chat.kick_member(user.id)
        await update.message.reply_text(f"🚫 @{user.username or user.first_name} foi banido após 3 avisos.")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /mute respondendo a uma mensagem do usuário.")
        return

    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=False)
    await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
    await update.message.reply_text(f"🔇 @{user.username or user.first_name} foi silenciado.")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /unmute respondendo a uma mensagem do usuário.")
        return

    user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True)
    await context.bot.restrict_chat_member(update.effective_chat.id, user.id, permissions=permissions)
    await update.message.reply_text(f"🔊 @{user.username or user.first_name} pode falar novamente.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Use /ban respondendo a uma mensagem do usuário.")
        return

    user = update.message.reply_to_message.from_user
    await update.message.chat.kick_member(user.id)
    await update.message.reply_text(f"🚫 @{user.username or user.first_name} foi banido.")

# =============== MAIN ===============
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("regras", regras))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))

    # Eventos
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), respostas_automaticas))

    print("✅ Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
