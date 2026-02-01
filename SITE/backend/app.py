from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

# Configura o Flask com a pasta de templates correta
app = Flask(__name__, template_folder='templates')
CORS(app)

COMPROVANTES_FILE = 'comprovantes.json'

def carregar_pedidos():
    """Lê os pedidos do arquivo JSON com tratamento de erro para arquivos vazios."""
    if not os.path.exists(COMPROVANTES_FILE):
        return {}
    
    try:
        with open(COMPROVANTES_FILE, 'r', encoding='utf-8') as f:
            conteudo = f.read().strip()
            if not conteudo:  # Se o arquivo estiver totalmente vazio
                return {}
            return json.loads(conteudo)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Erro ao carregar banco de dados: {e}")
        return {}

def salvar_pedidos(pedidos):
    """Salva os pedidos no arquivo JSON."""
    try:
        with open(COMPROVANTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(pedidos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar: {e}")

@app.route('/solicitar-liberacao', methods=['POST'])
def solicitar():
    data = request.json
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400
        
    pedidos = carregar_pedidos()
    ip = request.remote_addr
    
    pedidos[ip] = {
        "status": "pendente",
        "dispositivo": request.user_agent.platform if request.user_agent.platform else "Desconhecido",
        "hora": datetime.now().strftime("%H:%M:%S"),
        "dia": datetime.now().strftime("%d/%m/%Y"),
        "info": data.get("info_pix", "Sem identificação")
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
        return "Cliente Liberado com Sucesso!"
    return "IP nao encontrado.", 404

@app.route('/get-account')
def get_account():
    # Mantendo sua rota de entrega de contas
    return jsonify({"status": "estoque_vazio"}) 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)