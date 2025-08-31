import sqlite3

# Conecta ao banco de dados (ou cria se não existir)
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

# Garante que a tabela logs exista
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user TEXT,
    action TEXT
)
""")
conn.commit()

# ================= FUNÇÕES =================
def mostrar_todos_logs():
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    if logs:
        for log in logs:
            print(f"[{log[1]}] Usuário: {log[2]} | Ação: {log[3]}")
    else:
        print("Nenhum log registrado ainda.")

def filtrar_por_usuario(usuario):
    cursor.execute("SELECT * FROM logs WHERE user=? ORDER BY timestamp DESC", (usuario,))
    logs = cursor.fetchall()
    if logs:
        for log in logs:
            print(f"[{log[1]}] Usuário: {log[2]} | Ação: {log[3]}")
    else:
        print(f"Nenhum log encontrado para o usuário: {usuario}")

def filtrar_por_acao(acao):
    cursor.execute("SELECT * FROM logs WHERE action LIKE ? ORDER BY timestamp DESC", (f"%{acao}%",))
    logs = cursor.fetchall()
    if logs:
        for log in logs:
            print(f"[{log[1]}] Usuário: {log[2]} | Ação: {log[3]}")
    else:
        print(f"Nenhum log encontrado para a ação: {acao}")

# ================= MAIN =================
if __name__ == "__main__":
    print("===== TODOS OS LOGS =====")
    mostrar_todos_logs()

    # Exemplos de filtro:
    # print("\n===== Logs do usuário @fulano =====")
    # filtrar_por_usuario("fulano")
    
    # print("\n===== Logs de Flood =====")
    # filtrar_por_acao("Flood detectado")
