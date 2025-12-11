from flask import Blueprint, request, jsonify
from db import get_connection
import bcrypt

usuario_bp = Blueprint("usuario", __name__)

# ============================================================
# CADASTRAR USUÁRIO (CREATE)
# ============================================================
@usuario_bp.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()

    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")
    confirmar_senha = data.get("confirmar_senha")
    tipo = data.get("tipo")   # "ALUNO" ou "TUTOR"
    instituicao = data.get("instituicao")
    telefone = data.get("telefone")
    biografia = data.get("biografia")

    matricula = data.get("matricula")         # ALUNO
    registro_prof = data.get("registro_prof") # TUTOR


    # 1. Validar campos obrigatórios
    if not nome or not email or not senha or not confirmar_senha or not tipo:
        return jsonify({"status": 0, "erro": "Preencha todos os campos obrigatórios."}), 400

    # 2. Validar senha
    if senha != confirmar_senha:
        return jsonify({"status": 0, "erro": "As senhas não coincidem."}), 400

    # 3. Validar tipo
    if tipo not in ("ALUNO", "TUTOR"):
        return jsonify({"status": 0, "erro": "O tipo deve ser 'ALUNO' ou 'TUTOR'."}), 400

    # 4. Definir login_acesso
    if tipo == "ALUNO":
        if not matricula:
            return jsonify({"status": 0, "erro": "Matrícula é obrigatória para alunos."}), 400
        login_acesso = matricula

    else:  # TUTOR
        if not registro_prof:
            return jsonify({"status": 0, "erro": "Registro profissional é obrigatório para tutores."}), 400
        login_acesso = registro_prof

    # 5. Hash da senha
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 6. Inserir usuário
        sql_usuario = """
            INSERT INTO usuario 
            (nome, email, login_acesso, senha_hash, tipo, instituicao, telefone, biografia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_usuario;
        """

        cur.execute(sql_usuario, (
            nome, email, login_acesso, senha_hash, tipo, instituicao, telefone, biografia
        ))

        id_usuario = cur.fetchone()[0]

        # 7. Inserir tabela específica
        if tipo == "ALUNO":
            cur.execute(
                "INSERT INTO aluno (id_aluno, matricula) VALUES (%s, %s)",
                (id_usuario, matricula)
            )

        else:  # TUTOR
            cur.execute(
                "INSERT INTO tutor (id_tutor, registro_prof) VALUES (%s, %s)",
                (id_usuario, registro_prof)
            )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "status": 1,
            "mensagem": "Usuário cadastrado com sucesso!",
            "id_usuario": id_usuario
        }), 201

    except Exception as e:
        return jsonify({"status": 0, "erro": str(e)}), 500


@usuario_bp.get("/usuario/reed/<int:id_usuario>")
def obter_usuario(id_usuario):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id_usuario, nome, email, tipo, instituicao, telefone, biografia
            FROM usuario
            WHERE id_usuario = %s
        """, (id_usuario,))

        u = cur.fetchone()

        if not u:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        usuario = {
            "id_usuario": u[0],
            "nome": u[1],
            "email": u[2],
            "tipo": u[3],
            "instituicao": u[4],
            "telefone": u[5],
            "biografia": u[6]
        }

        cur.close()
        conn.close()

        return jsonify(usuario)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ============================================================
# ATUALIZAR USUÁRIO (UPDATE)
# ============================================================
@usuario_bp.patch("/usuario/update/<int:id_usuario>")
def atualizar_usuario(id_usuario):
    try:
        data = request.get_json()
        conn = get_connection()
        cur = conn.cursor()

        campos = []
        valores = []

        for campo in ["nome", "email", "instituicao", "telefone", "biografia"]:
            if campo in data:
                campos.append(f"{campo} = %s")
                valores.append(data[campo])

        if not campos:
            return jsonify({"erro": "Nada para atualizar"}), 400

        sql = f"UPDATE usuario SET {', '.join(campos)} WHERE id_usuario = %s"
        valores.append(id_usuario)

        cur.execute(sql, tuple(valores))

        if cur.rowcount == 0:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Usuário atualizado com sucesso!"})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ============================================================
# DELETAR (DELETE)
# ============================================================
@usuario_bp.delete("/usuario/delete/<int:id_usuario>")
def deletar_usuario(id_usuario):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))

        if cur.rowcount == 0:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Usuário deletado com sucesso!"})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
