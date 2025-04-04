"""
Importações

Flask: framework web para o python
sqllite3: para o banco de dados(embutido)
secrets: Para gerar códigos aleatórios

"""

from flask import Flask,  render_template, request, redirect, url_for
import sqlite3
import secrets


app = Flask(__name__) #é criado a aplicação flask
DB_NAME = "urls.db" #nome do arquivo do banco de dados

def  init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor() #Criei um cursor para operações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT NOT NULL UNIQUE
        )
    """) #executamos o comando  sql via cursor

    conn.commit() #confirmarmos
    conn.close() #fecha a conexão

init_db()#criamos o db aqui

# Rota para o formulário

@app.route("/")
def home():
    return render_template("index.html")

#Rota apra fazer o encurtamento da url

@app.route("/shorten", methods=["POST"])
def shorten_url():
    original_url = request.form.get("url")
    if not original_url:
        return "URL é obrigatória!", 400
    
    short_code = secrets.token_urlsafe(8)[:8] #codigo aleátorio de 8 caracter
    
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO urls (original_url, short_code) VALUES (?,?)",
                (original_url, short_code))
        conn.commit()
    except sqlite3.IntegrityError:
        # se o codigo existir, tenta novamente
        return redirect(url_for("home"))
    finally:
        conn.close()
        
    
    short_url = f"http://localhost:5000/{short_code}"
    return render_template("index.html", short_url=short_url)
    
# Rota pr redirecionar
@app.route("/<short_code>")
def redirect_to_url(short_code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    return "URL não encontrada!", 404

if __name__ == "__main__":
    app.run(debug=True)





