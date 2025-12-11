from flask import Flask
from flask_cors import CORS
from config import config

from rotas.login_routes import login_bp #CHAMANDO AS ROTAS E IMPORTANDO SEUS ENDPOINTS
from rotas.usuario_routes import usuario_bp




app = Flask(__name__)
app.config.from_object(config["desenvolvimento"])

CORS(app, resources={r"/*": {"origins": "*"}})  #Aplicar o CORS a todas as rotas, permitindo as origens diferentes acessar a WebApi

# registrando as rotas
app.register_blueprint(usuario_bp)
app.register_blueprint(login_bp)

@app.get("/")
def home():
    return "API RondonBot ativa!"

if __name__ == "__main__":
    app.run(port=app.config["API_BASE_PORT"], debug=True)
