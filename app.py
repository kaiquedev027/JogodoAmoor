from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from waitress import serve

app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

# Configurar banco de dados (executado automaticamente ao iniciar o app)
def setup_database():
    if not os.path.exists('db.sqlite'):
        conn = sqlite3.connect('db.sqlite')
        cursor = conn.cursor()

        # Criação da tabela de perguntas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
        ''')

        # Inserindo perguntas no banco de dados
        cursor.executemany('''
        INSERT INTO questions (question, answer)
        VALUES (?, ?)
        ''', [
            ("Qual foi o dia que nos conhecemos?", "10 de junho"),
            ("Qual é a minha cor favorita?", "azul"),
            ("Onde foi o nosso primeiro beijo?", "parque")
        ])

        conn.commit()
        conn.close()

# Inicializa a configuração do banco de dados ao rodar o app
setup_database()

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Página de perguntas
@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM questions WHERE id = ?', (question_id,)).fetchone()
    conn.close()
    
    # Redireciona para a página final se não houver mais perguntas
    if not question:
        return redirect(url_for('end'))
    
    if request.method == 'POST':
        answer = request.form['answer']
        # Valida a resposta
        if answer.lower() == question['answer'].lower():
            return redirect(url_for('question', question_id=question_id + 1))
        else:
            return render_template('question.html', question=question, question_id=question_id, error="Resposta errada! Tente novamente.")
    
    return render_template('question.html', question=question, question_id=question_id)

# Página final
@app.route('/end')
def end():
    return render_template('end.html')

# Configuração para inicializar o servidor
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=2004)
    app.run(debug=True)
