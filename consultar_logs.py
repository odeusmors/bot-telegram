import sqlite3

# Conecta ao banco de dados
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

def mostrar_todos_logs():
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    for log in logs:
        print(f"[{log[1]}] Usuário: {log[2]} | Ação: {log[3]}")

def filtrar_por_usuario(usuario):
    cursor.execute("SELECT * FROM logs WHERE user=? ORDER BY timestamp DESC", (usuario,))
    logs = cursor.fetchall()
    for log in logs:
        print(f"[{log[1]}] Usuário: {log[2]} | Ação: {log[3]}")

def filtrar_por_acao(acao):
    cursor.execute("SELECT * FROM logs WHERE action LIKE ? ORDER BY timestamp DESC", (f"%{acao}%",))
    logs = cursor.fetchall()
    for log in logs:
        print(f"[{log[1]}] Usuário: {log[2]} | Ação: {log[3]}")

if __name__ == "__main__":
    print("===== TODOS OS LOGS =====")
    mostrar_todos_logs()

    # Exemplo de filtro
    # print("===== Logs do usuário @fulano =====")
    # filtrar_por_usuario("fulano")
    
    # print("===== Logs de Flood =====")
    # filtrar_por_acao("Flood detectado")
