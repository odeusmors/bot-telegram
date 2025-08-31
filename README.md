# bot-telegram

📚 Documentação – Bot Telegram de Moderação
1️⃣ Estrutura do Projeto
my-bot-telegram/
│
├─ main.py          # Código principal do bot
├─ logs.txt         # Registro de atividades do bot
├─ requirements.txt # Dependências do projeto

2️⃣ Arquivos do Projeto
main.py

Contém todas as funções do bot, incluindo:

Moderação automática (filtro de links, flood, CAPSLOCK, palavras proibidas)

Comandos de admin (/warn, /mute, /unmute, /ban)

Boas-vindas automáticas a novos membros

Mensagens automáticas (respostas básicas)

Registro de logs

Servidor Flask para manter o bot online 24/7

Tecnologias usadas:

python-telegram-bot → Interação com a API do Telegram

Flask → Servidor web leve para manter o bot ativo no Replit

threading → Executa Flask em background sem interromper o bot

collections.defaultdict → Contagem de mensagens por usuário (anti-flood)

re → Filtros de palavras proibidas

time → Timestamp para logs

logs.txt

Armazena registros de todas as atividades do bot.

Criado automaticamente pelo bot na primeira ação de log ou você pode criar vazio.

Exemplo de entradas:

[2025-08-31 23:45:10] Novo membro DevNoshi entrou no grupo
[2025-08-31 23:47:02] Flood detectado de user123
[2025-08-31 23:48:15] @user456 recebeu /warn (1/3)


Serve para estudo, monitoramento e auditoria de ações dentro do grupo.

requirements.txt

Lista todas as dependências do projeto.

python-telegram-bot>=20.0
flask


Permite instalar todas as bibliotecas de uma vez:

pip install -r requirements.txt

3️⃣ Funcionalidades do Bot
Comandos básicos

/start → Mensagem inicial informando que o bot está ativo

/regras → Mostra as regras do grupo

/ajuda → Lista todos os comandos e funcionalidades do bot

Moderação automática

Bloqueio de links não permitidos

Bloqueio de palavras proibidas

Bloqueio de mensagens em CAPSLOCK

Anti-flood: impede que um usuário envie muitas mensagens rapidamente

Comandos de admin

/warn → Dá aviso a um usuário (3 avisos = ban automático)

/mute → Silencia o usuário

/unmute → Remove silêncio do usuário

/ban → Bane o usuário imediatamente

Obs: Para usar esses comandos, você deve ser admin do grupo e o bot também deve ter permissões de administrador.

Mensagens automáticas

Saudação de boas-vindas

Respostas simples a palavras como "oi", "olá" e "ajuda"

Logs de atividades

Todos os eventos importantes são salvos em logs.txt e exibidos no console.

Facilita análise e monitoramento do grupo.

4️⃣ Manter o bot online 24/7

Flask cria um pequeno servidor web dentro do bot:

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot online!"

Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()


UptimeRobot:

Ping do link público do Repl a cada 5 minutos

Evita que o Repl durma ou que o bot pare de funcionar

Link público do Repl exemplo:

https://1ff72b44-5f79-450f-be76-983b7b71ac43-00-16t8qtfbi7b1l.riker.replit.dev

5️⃣ Tecnologias utilizadas
Tecnologia	Função
Python 3	Linguagem principal do bot
python-telegram-bot	API do Telegram para interações e comandos
Flask	Servidor web leve para manter o bot ativo
threading	Executa Flask em paralelo com o bot
collections	Estruturas de dados para contagem de mensagens e avisos
re	Expressões regulares para detectar palavras proibidas
time	Timestamp para logs e monitoramento de flood
Replit	Ambiente de desenvolvimento e hospedagem gratuita
UptimeRobot	Ping automático para manter o bot online 24/7
6️⃣ Observações importantes

Alterações no código: Qualquer modificação no main.py precisa ser feita ou no Replit ou sincronizada com seu ambiente local.

Logs: Permitem monitorar o histórico do grupo e do bot, útil para estudo e auditoria.

Segurança: Apenas admins devem ter acesso a comandos de moderação. Você pode implementar verificação extra para limitar a apenas você (owner).

Escalabilidade: Quando o grupo crescer, é recomendado migrar para uma hospedagem paga (VPS ou cloud) para maior estabilidade.