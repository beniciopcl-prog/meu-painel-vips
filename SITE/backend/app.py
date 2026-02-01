from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

# Configura o Flask para procurar a pasta templates na mesma pasta deste arquivo
app = Flask(__name__, template_folder='templates')
CORS(app)

COMPROVANTES_FILE = 'comprovantes.json'

def carregar_pedidos():
    # Verifica se o arquivo existe e não está vazio
    if os.path.exists(COMPROVANTES_FILE) and os.path.getsize(COMPROVANTES_FILE) > 0:
        try:
            with open(COMPROVANTES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {} # Se der erro na leitura, retorna vazio
    return {}

def salvar_pedidos(pedidos):
    with open(COMPROVANTES_FILE, 'w') as f:
        json.dump(pedidos, f, indent=4)

@app.route('/solicitar-liberacao', methods=['POST'])
def solicitar():
    data = request.json
    pedidos = carregar_pedidos()
    ip = request.remote_addr
    
    pedidos[ip] = {
        "status": "pendente",
        "dispositivo": request.user_agent.platform if request.user_agent.platform else "Desconhecido",
        "hora": datetime.now().strftime("%H:%M:%S"),
        "dia": datetime.now().strftime("%d/%m/%Y"),
        "info": data.get("info_pix", "Sem info")
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
        return "Cliente Liberado! Pode avisar para atualizar a pagina."
    return "IP do cliente nao encontrado.", 404

@app.route('/get-account')
def get_account():
    return jsonify({"status": "estoque_vazio"}) 

if __name__ == '__main__':
    # Porta padrão para testes locais, a Render usa o gunicorn
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)