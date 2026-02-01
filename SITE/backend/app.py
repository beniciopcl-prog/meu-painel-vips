from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = 'database.txt'
COMPROVANTES_FILE = 'comprovantes.json'

def carregar_pedidos():
    if os.path.exists(COMPROVANTES_FILE):
        with open(COMPROVANTES_FILE, 'r') as f:
            return json.load(f)
    return {}

def salvar_pedidos(pedidos):
    with open(COMPROVANTES_FILE, 'w') as f:
        json.dump(pedidos, f)

@app.route('/solicitar-liberacao', methods=['POST'])
def solicitar():
    data = request.json
    pedidos = carregar_pedidos()
    ip = request.remote_addr
    
    pedidos[ip] = {
        "status": "pendente",
        "dispositivo": request.user_agent.platform,
        "hora": datetime.now().strftime("%H:%M:%S"),
        "dia": datetime.now().strftime("%d/%m/%Y"),
        "info": data.get("info_pix") # Nome ou ID da transação
    }
    salvar_pedidos(pedidos)
    return jsonify({"success": True})

@app.route('/checar-status')
def checar():
    pedidos = carregar_pedidos()
    ip = request.remote_addr
    status = pedidos.get(ip, {}).get("status", "inexistente")
    return jsonify({"status": status})

@app.route('/admin/painel-secreto')
def admin_painel():
    pedidos = carregar_pedidos()
    return render_template('admin_painel.html', pedidos=pedidos)

@app.route('/admin/liberar/<ip_cliente>')
def liberar_cliente(ip_cliente):
    pedidos = carregar_pedidos()
    if ip_cliente in pedidos:
        pedidos[ip_cliente]["status"] = "liberado"
        salvar_pedidos(pedidos)
        return "Cliente Liberado!"
    return "Erro", 404

# Sua rota antiga de extração continua aqui abaixo...
@app.route('/get-account')
def get_account():
    # ... (mantenha seu código de extração aqui)
    return jsonify({"status": "estoque_vazio"}) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)