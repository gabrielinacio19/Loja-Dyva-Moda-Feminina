import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify, send_from_directory, make_response

# Importa as funções de banco de dados
import banco


def hash_senha(senha: str) -> str:
	"""Gera hash SHA-256 da senha (simples para demo)."""
	return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def gerar_token() -> str:
	"""Gera um token seguro para sessão do usuário."""
	return secrets.token_urlsafe(32)


def criar_app() -> Flask:
	# Inicializa banco e cria dados iniciais (admin + produtos)
	banco.inicializar_banco()
	banco.criar_admin_e_produtos()

	app = Flask(__name__, static_folder=None)

	# ----------------------------
	# CORS básico para permitir testes via file:// e http://127.0.0.1:5000
	# ----------------------------
	@app.after_request
	def add_cors_headers(response):
		try:
			# Aplica CORS apenas para caminhos da API
			if request.path.startswith("/api"):
				origin = request.headers.get("Origin") or "*"
				response.headers["Access-Control-Allow-Origin"] = origin
				# Vary habilita cache correto por origem
				response.headers["Vary"] = "Origin"
				response.headers["Access-Control-Allow-Credentials"] = "false"
				response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
				response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
		except Exception:
			pass
		return response

	# Responde rapidamente às preflights da API
	@app.route('/api/<path:subpath>', methods=['OPTIONS'])
	def cors_preflight(subpath):
		resp = make_response('', 204)
		resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin") or "*"
		resp.headers["Vary"] = "Origin"
		resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
		resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
		return resp

	# ----------------------------
	# Funções auxiliares de autenticação
	# ----------------------------
	def usuario_atual() -> Optional[Dict[str, Any]]:
		"""
		Verifica autenticação através do token no cabeçalho da requisição.
		Retorna os dados do usuário logado ou None se não autenticado.
		"""
		auth = request.headers.get("Authorization", "").strip()
		if not auth.lower().startswith("bearer "):
			return None
		token = auth.split(" ", 1)[1].strip()
		sessao = banco.obter_sessao_por_token(token)
		if not sessao:
			return None
		usuario = banco.obter_usuario_por_id(sessao["usuario_id"])
		return usuario

	def requer_auth() -> Optional[Dict[str, Any]]:
		"""Verifica se o usuário está autenticado e retorna seus dados ou erro 401."""
		usuario = usuario_atual()
		if not usuario:
			resp = jsonify({"erro": "Não autenticado"})
			return make_response(resp, 401)
		return usuario

	def requer_admin(usr: Dict[str, Any]):
		if usr.get("role") != "admin":
			resp = jsonify({"erro": "Apenas admin"})
			return make_response(resp, 403)
		return None

	# ----------------------------
	# Rota raiz: retorna o site HTML
	# ----------------------------
	@app.get("/")
	def spa_index():
		pasta = os.path.dirname(os.path.abspath(__file__))
		return send_from_directory(pasta, "site.html")

	# Rota de verificação do servidor
	@app.get("/api/ping")
	def ping():
		return {"ok": True, "quando": datetime.utcnow().isoformat() + "Z"}

	# ----------------------------
	# Autenticação
	# ----------------------------
	@app.post("/api/registro")
	def registro():
		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except:
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		nome = (dados.get("nome") or "").strip()
		email = (dados.get("email") or "").strip().lower()
		senha = (dados.get("senha") or "").strip()

		if not nome or not email or not senha:
			return make_response(jsonify({"erro": "Informe nome, email e senha"}), 400)
		
		# Valida formato do email
		if "@" not in email or "." not in email.split("@")[-1]:
			return make_response(jsonify({"erro": "Email inválido"}), 400)
		
		# Valida tamanho mínimo da senha
		if len(senha) < 6:
			return make_response(jsonify({"erro": "Senha deve ter no mínimo 6 caracteres"}), 400)

		if banco.obter_usuario_por_email(email):
			return make_response(jsonify({"erro": "Email já cadastrado"}), 409)

		usuario_id = banco.criar_usuario(nome=nome, email=email, senha_hash=hash_senha(senha), role="user")
		return {"ok": True, "usuario_id": usuario_id}

	@app.post("/api/login")
	def login():
		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except:
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		email = (dados.get("email") or "").strip().lower()
		senha = (dados.get("senha") or "").strip()

		usuario = banco.obter_usuario_por_email(email)
		if not usuario or usuario["senha_hash"] != hash_senha(senha):
			return make_response(jsonify({"erro": "Credenciais inválidas"}), 401)

		token = gerar_token()
		banco.criar_sessao(token=token, usuario_id=usuario["id"]) 
		return {"ok": True, "token": token, "usuario": {"id": usuario["id"], "nome": usuario["nome"], "email": usuario["email"], "role": usuario["role"]}}

	@app.get("/api/me")
	def me():
		usr = usuario_atual()
		if not usr:
			return make_response(jsonify({"autenticado": False}), 200)
		return {"autenticado": True, "usuario": {"id": usr["id"], "nome": usr["nome"], "email": usr["email"], "role": usr["role"]}}

	# ----------------------------
	# Produtos
	# ----------------------------
	@app.get("/api/produtos")
	def listar_produtos():
		itens = banco.listar_produtos(ativos=True)
		return {"itens": itens}

	@app.get("/api/produtos/<int:produto_id>")
	def obter_produto(produto_id: int):
		prod = banco.obter_produto(produto_id)
		if not prod:
			return make_response(jsonify({"erro": "Produto não encontrado"}), 404)
		return prod

	@app.post("/api/produtos")
	def criar_produto():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr  # resposta 401
		erro = requer_admin(usr)
		if erro:
			return erro

		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except:
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		nome = (dados.get("nome") or "").strip()
		categoria = (dados.get("categoria") or "").strip()
		
		try:
			preco = float(dados.get("preco") or 0)
		except (ValueError, TypeError):
			return make_response(jsonify({"erro": "Preço inválido"}), 400)
			
		imagem = (dados.get("imagem") or "").strip()
		descricao = (dados.get("descricao") or "").strip() or None
		ativo = 1 if bool(dados.get("ativo", True)) else 0

		if not nome or preco <= 0:
			return make_response(jsonify({"erro": "Produto inválido"}), 400)

		pid = banco.criar_produto(nome, categoria, preco, imagem, ativo, descricao)

		# Salvar tamanhos (opcional)
		tamanhos = dados.get("tamanhos")
		if isinstance(tamanhos, list):
			try:
				banco.salvar_tamanhos(pid, tamanhos)
			except Exception:
				return make_response(jsonify({"erro": "Tamanhos inválidos"}), 400)

		return {"ok": True, "produto_id": pid}

	@app.put("/api/produtos/<int:produto_id>")
	def atualizar_produto(produto_id: int):
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		erro = requer_admin(usr)
		if erro:
			return erro

		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except:
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		nome = dados.get("nome")
		categoria = dados.get("categoria")
		preco = dados.get("preco")
		imagem = dados.get("imagem")
		ativo = dados.get("ativo")
		descricao = dados.get("descricao")

		ok = banco.atualizar_produto(produto_id, nome, categoria, preco, imagem, ativo, descricao)
		if not ok:
			return make_response(jsonify({"erro": "Produto não encontrado"}), 404)

		# Atualiza tamanhos se vierem no payload
		tamanhos = dados.get("tamanhos")
		if isinstance(tamanhos, list):
			try:
				banco.salvar_tamanhos(produto_id, tamanhos)
			except Exception:
				return make_response(jsonify({"erro": "Tamanhos inválidos"}), 400)
		return {"ok": True}

	@app.delete("/api/produtos/<int:produto_id>")
	def excluir_produto(produto_id: int):
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		erro = requer_admin(usr)
		if erro:
			return erro

		ok = banco.excluir_produto(produto_id)
		if not ok:
			return make_response(jsonify({"erro": "Produto não encontrado"}), 404)
		return {"ok": True}

	# ----------------------------
	# Carrinho
	# ----------------------------
	@app.get("/api/carrinho")
	def obter_carrinho():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		itens = banco.listar_carrinho(usr["id"])
		return {"itens": itens}

	@app.post("/api/carrinho/adicionar")
	def carrinho_adicionar():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
			produto_id = int(dados.get("produto_id"))
			tamanho = (dados.get("tamanho") or "").strip()
			quantidade = max(1, int(dados.get("quantidade", 1)))
		except (ValueError, TypeError, KeyError):
			return make_response(jsonify({"erro": "Dados inválidos"}), 400)
		if not tamanho:
			return make_response(jsonify({"erro": "Informe o tamanho"}), 400)
		
		ok = banco.adicionar_ao_carrinho(usr["id"], produto_id, tamanho, quantidade)
		if not ok:
			return make_response(jsonify({"erro": "Produto inválido ou inativo"}), 400)
		return {"ok": True}

	@app.post("/api/carrinho/remover")
	def carrinho_remover():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
			produto_id = int(dados.get("produto_id"))
			tamanho = (dados.get("tamanho") or "").strip() or None
		except (ValueError, TypeError, KeyError):
			return make_response(jsonify({"erro": "Dados inválidos"}), 400)
		
		banco.remover_do_carrinho(usr["id"], produto_id, tamanho)
		return {"ok": True}

	@app.post("/api/carrinho/limpar")
	def carrinho_limpar():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		banco.limpar_carrinho(usr["id"])
		return {"ok": True}

	# ----------------------------
	# Favoritos
	# ----------------------------
	@app.get("/api/favoritos")
	def listar_favoritos():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		itens = banco.listar_favoritos(usr["id"])
		return {"itens": itens}

	@app.post("/api/favoritos/toggle")
	def toggle_favorito():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
			produto_id = int(dados.get("produto_id"))
		except (ValueError, TypeError, KeyError):
			return make_response(jsonify({"erro": "Dados inválidos"}), 400)
			
		marcado = banco.alternar_favorito(usr["id"], produto_id)
		if marcado is None:
			return make_response(jsonify({"erro": "Produto inválido"}), 400)
		return {"ok": True, "favoritado": marcado}

	# ----------------------------
	# Pedidos
	# ----------------------------
	@app.post("/api/pedidos/finalizar")
	def finalizar_pedido():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		try:
			dados = request.get_json(force=True)
			if not dados:
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except:
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		metodo = (dados.get("metodo_pagamento") or "").strip()
		# Calcula total a partir do carrinho e tabela de produtos
		itens = banco.listar_carrinho(usr["id"])
		if not itens:
			return make_response(jsonify({"erro": "Carrinho vazio"}), 400)
		total = sum(i["preco"] * i["quantidade"] for i in itens)
		pedido_id = banco.criar_pedido(usr["id"], total, metodo or "Desconhecido", status="Pago")
		for i in itens:
			# valida e baixa estoque por tamanho
			if i.get("tamanho"):
				ok = banco.decrementar_estoque(i["produto_id"], i["tamanho"], i["quantidade"])
				if not ok:
					return make_response(jsonify({"erro": f"Sem estoque do tamanho {i['tamanho']}"}), 400)
			banco.adicionar_item_pedido(pedido_id, i["produto_id"], i["nome"], i["preco"], i["quantidade"], i.get("tamanho"))
		banco.limpar_carrinho(usr["id"])  # esvazia após pedido
		return {"ok": True, "pedido_id": pedido_id, "total": total}

	@app.get("/api/pedidos")
	def listar_pedidos():
		usr = requer_auth()
		if not isinstance(usr, dict):
			return usr
		pedidos = banco.listar_pedidos(usr["id"]) 
		return {"pedidos": pedidos}

	return app


if __name__ == "__main__":
	app = criar_app()
	print("\n" + "="*60)
	print("🚀 SERVIDOR DYVA INICIADO COM SUCESSO!")
	print("="*60)
	print(f"📍 Acesse: http://127.0.0.1:5000")
	print(f"👤 Admin: admin@dyva.com | Senha: 123456")
	print(f"💾 Banco de dados: dyva.db")
	print("="*60 + "\n")
	# Servidor roda em http://127.0.0.1:5000
	app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)

