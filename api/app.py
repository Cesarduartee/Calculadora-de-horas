from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
CORS(app)
Swagger(app)


def banco():
    return sqlite3.connect("horas.db")


def criar_tabela():
    con = banco()
    con.execute("""CREATE TABLE IF NOT EXISTS calculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inicio TEXT,
        duracao TEXT,
        saida TEXT
    )""")
    con.commit()
    con.close()


@app.route("/calculos", methods=["POST"])
def calcular():
    """Calcula e salva um horário
    ---
    parameters:
      - in: body
        name: dados
        schema:
          type: object
          properties:
            inicio: {type: string, example: "08:00"}
            duracao: {type: string, example: "09:30"}
    responses:
      201: {description: Cálculo salvo}
      400: {description: Dados inválidos}
    """
    dados = request.json
    inicio = dados.get("inicio")
    duracao = dados.get("duracao")

    if duracao not in ["09:30", "10:00"]:
        return jsonify({"erro": "Duração inválida"}), 400

    try:
        hora = datetime.strptime(inicio, "%H:%M")
    except:
        return jsonify({"erro": "Hora inválida"}), 400

    h, m = duracao.split(":")
    fim = hora + timedelta(hours=int(h), minutes=int(m))
    saida = fim.strftime("%H:%M")

    con = banco()
    cursor = con.execute(
        "INSERT INTO calculos (inicio, duracao, saida) VALUES (?, ?, ?)",
        (inicio, duracao, saida)
    )
    con.commit()
    id_novo = cursor.lastrowid
    con.close()

    return jsonify({"id": id_novo, "inicio": inicio, "duracao": duracao, "saida": saida}), 201


@app.route("/calculos", methods=["GET"])
def listar():
    """Lista os cálculos
    ---
    responses:
      200: {description: Lista de cálculos}
    """
    con = banco()
    dados = con.execute("SELECT * FROM calculos ORDER BY id DESC").fetchall()
    con.close()

    lista = []
    for item in dados:
        lista.append({"id": item[0], "inicio": item[1], "duracao": item[2], "saida": item[3]})
    return jsonify(lista)


@app.route("/calculos/<int:id>", methods=["GET"])
def buscar(id):
    """Busca um cálculo pelo id
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200: {description: Cálculo encontrado}
      404: {description: Não encontrado}
    """
    con = banco()
    item = con.execute("SELECT * FROM calculos WHERE id = ?", (id,)).fetchone()
    con.close()

    if not item:
        return jsonify({"erro": "Não encontrado"}), 404

    return jsonify({"id": item[0], "inicio": item[1], "duracao": item[2], "saida": item[3]})


@app.route("/calculos/<int:id>", methods=["DELETE"])
def excluir(id):
    """Exclui um cálculo
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200: {description: Cálculo excluído}
    """
    con = banco()
    con.execute("DELETE FROM calculos WHERE id = ?", (id,))
    con.commit()
    con.close()
    return jsonify({"mensagem": "Excluído"})


if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)
