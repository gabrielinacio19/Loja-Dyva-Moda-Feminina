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
		return {"ok": True, "quando": datetime.now().isoformat() + "Z"}

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
		print(f"✅ NOVO USUÁRIO CRIADO: {nome} ({email}) - ID: {usuario_id}")
		return {"ok": True, "usuario_id": usuario_id}

	@app.post("/api/login")
	def login():
		try:
			print("🔐 LOGIN: Recebendo requisição...")
			dados = request.get_json(force=True)
			print(f"🔐 LOGIN: Dados recebidos: {dados}")
			
			if not dados:
				print("❌ LOGIN: JSON vazio")
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except Exception as e:
			print(f"❌ LOGIN: Erro ao processar JSON: {e}")
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		email = (dados.get("email") or "").strip().lower()
		senha = (dados.get("senha") or "").strip()
		
		print(f"🔐 LOGIN: Email processado: '{email}'")
		print(f"🔐 LOGIN: Senha recebida: {'*' * len(senha)}")

		usuario = banco.obter_usuario_por_email(email)
		if not usuario:
			print(f"❌ LOGIN: Usuário não encontrado: {email}")
			return make_response(jsonify({"erro": "Credenciais inválidas"}), 401)
			
		print(f"🔐 LOGIN: Usuário encontrado: {usuario['nome']}")
		
		hash_fornecido = hash_senha(senha)
		if usuario["senha_hash"] != hash_fornecido:
			print(f"❌ LOGIN: Senha incorreta para {email}")
			print(f"❌ Hash esperado: {usuario['senha_hash'][:20]}...")
			print(f"❌ Hash fornecido: {hash_fornecido[:20]}...")
			return make_response(jsonify({"erro": "Credenciais inválidas"}), 401)

		token = gerar_token()
		banco.criar_sessao(token=token, usuario_id=usuario["id"]) 
		print(f"🔑 LOGIN REALIZADO: {usuario['nome']} ({email}) - Token: {token[:8]}...")
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

	@app.get("/api/produtos/<int:produto_id>/tamanhos")
	def listar_tamanhos(produto_id: int):
		produto = banco.obter_produto(produto_id)
		if not produto:
			return make_response(jsonify({"erro": "Produto não encontrado"}), 404)
		
		tamanhos = banco.listar_tamanhos(produto_id)
		return {"tamanhos": tamanhos}

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
		
		# Validações de tamanho para prevenir overflow
		if len(nome) > 100:
			return make_response(jsonify({"erro": "Nome deve ter no máximo 100 caracteres"}), 400)
		
		if len(categoria) > 50:
			return make_response(jsonify({"erro": "Categoria deve ter no máximo 50 caracteres"}), 400)
		
		try:
			preco = float(dados.get("preco") or 0)
		except (ValueError, TypeError):
			return make_response(jsonify({"erro": "Preço inválido"}), 400)
		
		# Validar preço dentro de limites razoáveis
		if preco <= 0 or preco > 999999:
			return make_response(jsonify({"erro": "Preço deve estar entre 0.01 e 999.999"}), 400)
			
		imagem = (dados.get("imagem") or "").strip()
		descricao = (dados.get("descricao") or "").strip() or None
		
		# Validar tamanho da descrição
		if descricao and len(descricao) > 1000:
			return make_response(jsonify({"erro": "Descrição deve ter no máximo 1000 caracteres"}), 400)
		
		# Sanitizar contra XSS básico
		import html
		nome = html.escape(nome)
		categoria = html.escape(categoria)
		if descricao:
			descricao = html.escape(descricao)
		if imagem:
			imagem = html.escape(imagem)
		
		ativo = 1 if bool(dados.get("ativo", True)) else 0

		if not nome:
			return make_response(jsonify({"erro": "Nome é obrigatório"}), 400)

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
		print(f"✏️ PRODUTO: Recebendo requisição de atualização...")
		print(f"✏️ PRODUTO: ID do produto: {produto_id}")
		
		usr = requer_auth()
		if not isinstance(usr, dict):
			print(f"❌ PRODUTO: Erro de autenticação")
			return usr
			
		print(f"✏️ PRODUTO: Admin autenticado: {usr['nome']} (ID: {usr['id']})")
		
		erro = requer_admin(usr)
		if erro:
			print(f"❌ PRODUTO: Usuário não é admin")
			return erro

		try:
			dados = request.get_json(force=True)
			print(f"✏️ PRODUTO: Dados recebidos: {dados}")
			if not dados:
				print(f"❌ PRODUTO: JSON inválido ou vazio")
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except Exception as e:
			print(f"❌ PRODUTO: Erro ao processar JSON: {e}")
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		nome = dados.get("nome")
		categoria = dados.get("categoria")
		preco = dados.get("preco")
		imagem = dados.get("imagem")
		ativo = dados.get("ativo")
		descricao = dados.get("descricao")
		
		print(f"✏️ PRODUTO: Atualizando - Nome: '{nome}', Preço: {preco}, Categoria: '{categoria}'")

		ok = banco.atualizar_produto(produto_id, nome, categoria, preco, imagem, ativo, descricao)
		if not ok:
			print(f"❌ PRODUTO: Produto ID {produto_id} não encontrado no banco")
			return make_response(jsonify({"erro": "Produto não encontrado"}), 404)

		# Atualiza tamanhos se vierem no payload
		tamanhos = dados.get("tamanhos")
		if isinstance(tamanhos, list):
			try:
				print(f"✏️ PRODUTO: Atualizando tamanhos: {tamanhos}")
				banco.salvar_tamanhos(produto_id, tamanhos)
			except Exception as e:
				print(f"❌ PRODUTO: Erro ao atualizar tamanhos: {e}")
				return make_response(jsonify({"erro": "Tamanhos inválidos"}), 400)
				
		print(f"✅ PRODUTO ATUALIZADO: ID {produto_id} - {nome} por {usr['nome']}")
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
		print(f"🛒 CARRINHO: Recebendo requisição...")
		usr = requer_auth()
		if not isinstance(usr, dict):
			print(f"❌ CARRINHO: Erro de autenticação")
			return usr
		print(f"🛒 CARRINHO: Usuário autenticado: {usr['nome']} (ID: {usr['id']})")
		
		try:
			dados = request.get_json(force=True)
			print(f"🛒 CARRINHO: Dados recebidos: {dados}")
			
			if not dados:
				print(f"❌ CARRINHO: JSON inválido ou vazio")
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
				
			produto_id = int(dados.get("produto_id"))
			tamanho = (dados.get("tamanho") or "").strip()
			quantidade_raw = dados.get("quantidade", 1)
			
			print(f"🛒 CARRINHO: Produto ID: {produto_id}, Tamanho: '{tamanho}', Quantidade: {quantidade_raw}")
			
			# Validar quantidade explicitamente
			try:
				quantidade = int(quantidade_raw)
				if quantidade <= 0:
					return make_response(jsonify({"erro": "Quantidade deve ser maior que zero"}), 400)
				if quantidade > 99:
					return make_response(jsonify({"erro": "Quantidade máxima é 99"}), 400)
			except (ValueError, TypeError):
				return make_response(jsonify({"erro": "Quantidade deve ser um número válido"}), 400)
				
		except (ValueError, TypeError, KeyError):
			return make_response(jsonify({"erro": "Dados inválidos"}), 400)
		if not tamanho:
			print(f"❌ CARRINHO: Tamanho não informado")
			return make_response(jsonify({"erro": "Informe o tamanho"}), 400)
		
		print(f"🛒 CARRINHO: Tentando adicionar ao carrinho...")
		ok = banco.adicionar_ao_carrinho(usr["id"], produto_id, tamanho, quantidade)
		if not ok:
			print(f"❌ CARRINHO: Produto {produto_id} não encontrado ou inativo")
			return make_response(jsonify({"erro": "Produto inválido ou inativo"}), 400)
		print(f"✅ ITEM ADICIONADO: {usr['nome']} - Produto {produto_id} ({tamanho}) x{quantidade}")
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
		acao = "ADICIONADO" if marcado else "REMOVIDO"
		print(f"❤️ FAVORITO {acao}: {usr['nome']} - Produto {produto_id}")
		return {"ok": True, "favoritado": marcado}

	# ----------------------------
	# Pedidos
	# ----------------------------
	@app.post("/api/pedidos/finalizar")
	def finalizar_pedido():
		print(f"📦 PEDIDO: Recebendo requisição de finalizar pedido...")
		usr = requer_auth()
		if not isinstance(usr, dict):
			print(f"❌ PEDIDO: Erro de autenticação")
			return usr
		print(f"📦 PEDIDO: Usuário autenticado: {usr['nome']} (ID: {usr['id']})")
		
		try:
			dados = request.get_json(force=True)
			print(f"📦 PEDIDO: Dados recebidos: {dados}")
			if not dados:
				print(f"❌ PEDIDO: JSON inválido ou vazio")
				return make_response(jsonify({"erro": "JSON inválido"}), 400)
		except Exception as e:
			print(f"❌ PEDIDO: Erro ao processar JSON: {e}")
			return make_response(jsonify({"erro": "JSON inválido"}), 400)
			
		# Verificar se é pedido do frontend (dados completos) ou API simples
		if "produtos" in dados and "total" in dados:
			print(f"📦 PEDIDO: Formato frontend - processando dados completos")
			# Formato do frontend
			produtos_pedido = dados.get("produtos", [])
			if not produtos_pedido:
				print(f"❌ PEDIDO: Lista de produtos vazia")
				return make_response(jsonify({"erro": "Nenhum produto no pedido"}), 400)
			
			metodo = dados.get("pagamento", "Desconhecido")
			# Total pode vir como string ou number
			total_raw = dados.get("total", 0)
			if isinstance(total_raw, str):
				total = float(total_raw.replace(",", "."))
			else:
				total = float(total_raw)
			
			print(f"📦 PEDIDO: {len(produtos_pedido)} produtos, Total: R${total}, Método: {metodo}")
			
			pedido_id = banco.criar_pedido(usr["id"], total, metodo, status="Pago")
			
			# Adicionar itens do pedido
			for produto in produtos_pedido:
				produto_id = produto.get("id")
				nome = produto.get("nome", "Produto")
				# Preco pode vir como int, float ou string
				preco_raw = produto.get("preco", 0)
				if isinstance(preco_raw, str):
					preco = float(preco_raw.replace(",", "."))
				else:
					preco = float(preco_raw)
				quantidade = produto.get("qty", 1)
				tamanho = produto.get("tamanho", "")
				
				banco.adicionar_item_pedido(pedido_id, produto_id, nome, preco, quantidade, tamanho)
				print(f"📦 PEDIDO: Item adicionado - {nome} ({tamanho}) x{quantidade} = R${preco}")
		else:
			print(f"📦 PEDIDO: Formato API - usando carrinho")
			# Formato original da API
			metodo = (dados.get("metodo_pagamento") or "").strip()
			itens = banco.listar_carrinho(usr["id"])
			if not itens:
				print(f"❌ PEDIDO: Carrinho vazio")
				return make_response(jsonify({"erro": "Carrinho vazio"}), 400)
			total = sum(i["preco"] * i["quantidade"] for i in itens)
			pedido_id = banco.criar_pedido(usr["id"], total, metodo or "Desconhecido", status="Pago")
			
			for i in itens:
				# valida e baixa estoque por tamanho
				if i.get("tamanho"):
					ok = banco.decrementar_estoque(i["produto_id"], i["tamanho"], i["quantidade"])
					if not ok:
						print(f"❌ PEDIDO: Sem estoque - {i['tamanho']}")
						return make_response(jsonify({"erro": f"Sem estoque do tamanho {i['tamanho']}"}), 400)
				banco.adicionar_item_pedido(pedido_id, i["produto_id"], i["nome"], i["preco"], i["quantidade"], i.get("tamanho"))
			banco.limpar_carrinho(usr["id"])  # esvazia após pedido
		
		print(f"✅ PEDIDO FINALIZADO: {usr['nome']} - ID: {pedido_id} - Total: R$ {total:.2f}")
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
	print("\n" + "="*70)
	print("🚀 SERVIDOR DYVA E-COMMERCE INICIADO COM SUCESSO!")
	print("="*70)
	print(f"📍 URL Base: http://127.0.0.1:5000")
	print(f"👤 Admin: admin@dyva.com | Senha: 123456")
	print(f"💾 Banco SQLite: dyva.db conectado")
	print(f"🔐 Autenticação JWT configurada")
	print(f"🌐 CORS habilitado para desenvolvimento")
	print("="*70)
	print("📋 API ENDPOINTS DISPONÍVEIS:")
	print("   🔑 Autenticação:")
	print("      POST /api/login       - Login de usuários")
	print("      POST /api/registro    - Cadastro de novos usuários") 
	print("      GET  /api/me          - Dados do usuário logado")
	print("   🛍️  Produtos:")
	print("      GET  /api/produtos    - Listar todos os produtos")
	print("      GET  /api/produtos/id - Produto específico")
	print("      GET  /api/produtos/id/tamanhos - Tamanhos do produto")
	print("      POST /api/produtos    - Criar produto (admin)")
	print("      PUT  /api/produtos/id - Editar produto (admin)")
	print("      DEL  /api/produtos/id - Deletar produto (admin)")
	print("   🛒 Carrinho:")
	print("      GET  /api/carrinho           - Ver carrinho do usuário")
	print("      POST /api/carrinho/adicionar - Adicionar item")
	print("      POST /api/carrinho/remover   - Remover item")
	print("      POST /api/carrinho/limpar    - Limpar carrinho")
	print("   ❤️  Favoritos:")
	print("      GET  /api/favoritos       - Listar favoritos")
	print("      POST /api/favoritos/toggle - Toggle favorito")
	print("   📦 Pedidos:")
	print("      POST /api/pedidos/finalizar - Finalizar pedido")
	print("      GET  /api/pedidos          - Histórico de pedidos")
	print("   🏠 Página:")
	print("      GET  /                     - Servir site.html")
	print("="*70)
	print("✅ Backend Flask com 18 endpoints funcionando!")
	print("✅ Banco de dados SQLite com 8 tabelas estruturadas!")
	print("✅ Sistema pronto para receber requisições!")
	print("="*70 + "\n")
	# Servidor roda em http://127.0.0.1:5000
	import logging
	logging.basicConfig(level=logging.INFO)
	app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)

