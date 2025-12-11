from flask import Blueprint, request, jsonify
from db import get_connection
import bcrypt  # necessário para validar a senha

login_bp = Blueprint("login", __name__)

@login_bp.route("/api/autenticarLogin", methods=["POST"])
def autenticar_login():
    data = request.get_json()

    login_input = data.get("login")   # email OU matricula OU registro_prof
    senha = data.get("senha")

    # 1. VALIDAÇÃO SIMPLES
    if not login_input or not senha:
        return jsonify({
            "status": 0,
            "aviso": "Login e senha são obrigatórios."
        }), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 2. BUSCAR USUÁRIO VIA FUNCTION
        cur.execute("SELECT * FROM f_buscar_usuario_login(%s)", (login_input,))
        resultado = cur.fetchone()

        if not resultado:
            return jsonify({
                "status": 0,
                "aviso": "Usuário não encontrado."
            }), 404

        # A function deve retornar:
        # id_usuario, nome, email, tipo, senha_hash, login_acesso
        id_usuario, nome, email, tipo, senha_hash, login_acesso = resultado

        # 3. COMPARAR senha fornecida x senha hash armazenada
        senha_valida = bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))

        if not senha_valida:
            return jsonify({
                "status": 0,
                "aviso": "Senha incorreta."
            }), 401

        # 4. LOGIN OK
        return jsonify({
            "status": 1,
            "mensagem": "Login realizado com sucesso!",
        }), 200

    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({
            "status": 0,
            "aviso": "Erro interno no servidor."
        }), 500

    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
