import os
import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

ARQUIVO_DB = os.path.join(os.path.dirname(__file__), "dyva.db")


def conectar() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(ARQUIVO_DB, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Erro ao conectar banco: {e}")
        raise


def inicializar_banco() -> None:
    """Cria tabelas caso não existam."""
    try:
        with conectar() as conn:
            cur = conn.cursor()
        # Usuários e sessões
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessoes (
                token TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                criado_em TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
            """
        )

        # Produtos (adiciona coluna descricao se não existir)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT,
                preco REAL NOT NULL,
                imagem TEXT,
                ativo INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        # Adiciona coluna descricao se não existir
        cur.execute("PRAGMA table_info(produtos)")
        colunas = [r[1] for r in cur.fetchall()]
        if "descricao" not in colunas:
            cur.execute("ALTER TABLE produtos ADD COLUMN descricao TEXT")

        # Tamanhos por produto
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos_tamanhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tamanho TEXT NOT NULL,
                estoque INTEGER NOT NULL DEFAULT 0,
                UNIQUE(produto_id, tamanho),
                FOREIGN KEY(produto_id) REFERENCES produtos(id)
            )
            """
        )

        # Carrinho e favoritos
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS carrinhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                tamanho TEXT,
                quantidade INTEGER NOT NULL,
                UNIQUE(usuario_id, produto_id, tamanho),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY(produto_id) REFERENCES produtos(id)
            )
            """
        )
        # Adiciona coluna tamanho em carrinhos se não existir
        cur.execute("PRAGMA table_info(carrinhos)")
        cols_car = [r[1] for r in cur.fetchall()]
        if "tamanho" not in cols_car:
            try:
                cur.execute("ALTER TABLE carrinhos ADD COLUMN tamanho TEXT")
            except Exception:
                pass
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS favoritos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                UNIQUE(usuario_id, produto_id),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY(produto_id) REFERENCES produtos(id)
            )
            """
        )

        # Pedidos
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                total REAL NOT NULL,
                metodo_pagamento TEXT NOT NULL,
                status TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pedido_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                tamanho TEXT,
                quantidade INTEGER NOT NULL,
                FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
                FOREIGN KEY(produto_id) REFERENCES produtos(id)
            )
            """
        )
        # Adiciona coluna tamanho em pedido_itens se não existir
        cur.execute("PRAGMA table_info(pedido_itens)")
        cols_pi = [r[1] for r in cur.fetchall()]
        if "tamanho" not in cols_pi:
            try:
                cur.execute("ALTER TABLE pedido_itens ADD COLUMN tamanho TEXT")
            except Exception:
                pass
        conn.commit()
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")
        raise


def criar_admin_e_produtos() -> None:
    """Cria usuário admin padrão e produtos iniciais se o banco estiver vazio."""
    from hashlib import sha256
    admin_email = "admin@dyva.com"
    admin_senha_hash = sha256("123456".encode("utf-8")).hexdigest()

    with conectar() as conn:
        cur = conn.cursor()
        # Admin
        cur.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (?, ?, ?, 'admin')",
                ("Admin", admin_email, admin_senha_hash),
            )
            
        # Usuário comum padrão
        user_email = "usuario@teste.com"
        user_senha_hash = sha256("senha123".encode("utf-8")).hexdigest()
        cur.execute("SELECT id FROM usuarios WHERE email = ?", (user_email,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (?, ?, ?, 'user')",
                ("Usuário Teste", user_email, user_senha_hash),
            )

        # Produtos (só se não houver nenhum)
        cur.execute("SELECT COUNT(*) AS c FROM produtos")
        c = cur.fetchone()["c"]
        if c == 0:
            produtos_iniciais = [
                ("Macaquinho Floral", "Macaquinhos", 129.90, "https://i.ibb.co/7zL2Z3W/macaquinho.jpg", 1, "Macaquinho floral leve, ideal para o dia a dia."),
                ("Cropped Rosa", "Croppeds", 79.90, "https://i.ibb.co/7Cs2YrK/cropped.jpg", 1, "Cropped em malha canelada com alto conforto."),
                ("Saia Midi", "Saias", 99.90, "https://i.ibb.co/Wz7t2mP/saia.jpg", 1, "Saia midi com caimento elegante."),
                ("Blusa Noir", "Blusas", 69.90, "https://i.ibb.co/2W6r0GJ/blusa.jpg", 1, "Blusa básica preta, combina com tudo."),
            ]
            cur.executemany(
                "INSERT INTO produtos (nome, categoria, preco, imagem, ativo, descricao) VALUES (?, ?, ?, ?, ?, ?)",
                produtos_iniciais,
            )
            # tamanhos padrão para cada produto
            cur.execute("SELECT id FROM produtos")
            ids = [r[0] for r in cur.fetchall()]
            tamanhos_padrao: List[Tuple[int, str, int]] = []
            for pid in ids:
                for tam, est in [("PP", 10), ("P", 10), ("M", 10), ("G", 10), ("GG", 10)]:
                    tamanhos_padrao.append((pid, tam, est))
            cur.executemany(
                "INSERT OR IGNORE INTO produtos_tamanhos (produto_id, tamanho, estoque) VALUES (?, ?, ?)",
                tamanhos_padrao,
            )
        conn.commit()


# ---------------------------
# Usuários e sessões
# ---------------------------

def criar_usuario(nome: str, email: str, senha_hash: str, role: str = "user") -> int:
    try:
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, role),
            )
            conn.commit()
            return cur.lastrowid
    except sqlite3.IntegrityError:
        print(f"Email já existe: {email}")
        raise
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        raise


def obter_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    try:
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None


def obter_usuario_por_id(usuario_id: int) -> Optional[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def criar_sessao(token: str, usuario_id: int) -> None:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO sessoes (token, usuario_id, criado_em) VALUES (?, ?, ?)",
            (token, usuario_id, datetime.utcnow().isoformat() + "Z"),
        )
        conn.commit()


def obter_sessao_por_token(token: str) -> Optional[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sessoes WHERE token = ?", (token,))
        row = cur.fetchone()
        return dict(row) if row else None


# ---------------------------
# Produtos
# ---------------------------

def listar_produtos(ativos: bool = True) -> List[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        if ativos:
            cur.execute("SELECT * FROM produtos WHERE ativo = 1 ORDER BY id ASC")
        else:
            cur.execute("SELECT * FROM produtos ORDER BY id ASC")
        return [dict(r) for r in cur.fetchall()]


def criar_produto(nome: str, categoria: str, preco: float, imagem: str, ativo: int = 1, descricao: Optional[str] = None) -> int:
    try:
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO produtos (nome, categoria, preco, imagem, ativo, descricao) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, categoria, float(preco), imagem, ativo, descricao),
            )
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        raise


def atualizar_produto(produto_id: int, nome=None, categoria=None, preco=None, imagem=None, ativo=None, descricao=None) -> bool:
    try:
        campos = []
        params = []
        if nome is not None:
            campos.append("nome = ?")
            params.append(nome)
        if categoria is not None:
            campos.append("categoria = ?")
            params.append(categoria)
        if preco is not None:
            campos.append("preco = ?")
            try:
                params.append(float(preco))
            except (ValueError, TypeError):
                print(f"Preço inválido: {preco}")
                return False
        if imagem is not None:
            campos.append("imagem = ?")
            params.append(imagem)
        if ativo is not None:
            campos.append("ativo = ?")
            params.append(1 if bool(ativo) else 0)
        if descricao is not None:
            campos.append("descricao = ?")
            params.append(descricao)

        if not campos:
            return False

        params.append(produto_id)
        with conectar() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE produtos SET {', '.join(campos)} WHERE id = ?", params)
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        return False


def excluir_produto(produto_id: int) -> bool:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        return cur.rowcount > 0


def obter_produto(produto_id: int) -> Optional[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM produtos WHERE id = ? AND ativo = 1", (produto_id,))
        row = cur.fetchone()
        if not row:
            return None
        prod = dict(row)
        # tamanhos em ordem correta (PP, P, M, G, GG)
        cur.execute("""
            SELECT tamanho, estoque FROM produtos_tamanhos 
            WHERE produto_id = ? 
            ORDER BY 
                CASE tamanho 
                    WHEN 'PP' THEN 1 
                    WHEN 'P' THEN 2 
                    WHEN 'M' THEN 3 
                    WHEN 'G' THEN 4 
                    WHEN 'GG' THEN 5 
                    ELSE 6 
                END
        """, (produto_id,))
        prod["tamanhos"] = [
            {"tamanho": r[0], "estoque": int(r[1])}
            for r in cur.fetchall()
        ]
        return prod


def salvar_tamanhos(produto_id: int, tamanhos: List[Dict[str, Any]]) -> None:
    """Substitui os tamanhos de um produto pela lista informada."""
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM produtos_tamanhos WHERE produto_id = ?", (produto_id,))
        for t in tamanhos:
            tam = str(t.get("tamanho", "")).strip()
            est = int(t.get("estoque", 0))
            if tam:
                cur.execute(
                    "INSERT INTO produtos_tamanhos (produto_id, tamanho, estoque) VALUES (?, ?, ?)",
                    (produto_id, tam, est),
                )
        conn.commit()

def obter_tamanho(produto_id: int, tamanho: str) -> Optional[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT tamanho, estoque FROM produtos_tamanhos WHERE produto_id = ? AND tamanho = ?",
            (produto_id, tamanho),
        )
        row = cur.fetchone()
        return {"tamanho": row[0], "estoque": int(row[1])} if row else None

def listar_tamanhos(produto_id: int) -> List[Dict[str, Any]]:
    """Lista todos os tamanhos disponíveis para um produto."""
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT tamanho, estoque FROM produtos_tamanhos WHERE produto_id = ? ORDER BY tamanho",
            (produto_id,),
        )
        rows = cur.fetchall()
        return [{"tamanho": row[0], "estoque": int(row[1])} for row in rows]


# ---------------------------
# Carrinho
# ---------------------------

def listar_carrinho(usuario_id: int) -> List[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.produto_id, p.nome, p.preco, p.imagem, c.tamanho, c.quantidade
            FROM carrinhos c
            JOIN produtos p ON p.id = c.produto_id
            WHERE c.usuario_id = ? AND p.ativo = 1
            ORDER BY c.id DESC
            """,
            (usuario_id,),
        )
        return [
            {
                "produto_id": r["produto_id"],
                "nome": r["nome"],
                "preco": float(r["preco"]),
                "imagem": r["imagem"],
                "tamanho": r["tamanho"],
                "quantidade": int(r["quantidade"]),
            }
            for r in cur.fetchall()
        ]


def adicionar_ao_carrinho(usuario_id: int, produto_id: int, tamanho: str, quantidade: int) -> bool:
    prod = obter_produto(produto_id)
    if not prod:
        return False
    # valida tamanho
    tinfo = obter_tamanho(produto_id, tamanho)
    if not tinfo:
        return False
    with conectar() as conn:
        cur = conn.cursor()
        # Se já existe, soma quantidade
        cur.execute(
            "SELECT quantidade FROM carrinhos WHERE usuario_id = ? AND produto_id = ? AND tamanho = ?",
            (usuario_id, produto_id, tamanho),
        )
        row = cur.fetchone()
        if row:
            nova = int(row["quantidade"]) + int(quantidade)
            cur.execute(
                "UPDATE carrinhos SET quantidade = ? WHERE usuario_id = ? AND produto_id = ? AND tamanho = ?",
                (nova, usuario_id, produto_id, tamanho),
            )
        else:
            cur.execute(
                "INSERT INTO carrinhos (usuario_id, produto_id, tamanho, quantidade) VALUES (?, ?, ?, ?)",
                (usuario_id, produto_id, tamanho, int(quantidade)),
            )
        conn.commit()
        return True


def remover_do_carrinho(usuario_id: int, produto_id: int, tamanho: Optional[str] = None) -> None:
    with conectar() as conn:
        cur = conn.cursor()
        if tamanho is None:
            cur.execute(
                "DELETE FROM carrinhos WHERE usuario_id = ? AND produto_id = ?",
                (usuario_id, produto_id),
            )
        else:
            cur.execute(
                "DELETE FROM carrinhos WHERE usuario_id = ? AND produto_id = ? AND tamanho = ?",
                (usuario_id, produto_id, tamanho),
            )
        conn.commit()


def limpar_carrinho(usuario_id: int) -> None:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM carrinhos WHERE usuario_id = ?", (usuario_id,))
        conn.commit()


# ---------------------------
# Favoritos
# ---------------------------

def listar_favoritos(usuario_id: int) -> List[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT f.produto_id, p.nome, p.preco, p.imagem
            FROM favoritos f
            JOIN produtos p ON p.id = f.produto_id
            WHERE f.usuario_id = ? AND p.ativo = 1
            ORDER BY f.id DESC
            """,
            (usuario_id,),
        )
        return [
            {
                "produto_id": r["produto_id"],
                "nome": r["nome"],
                "preco": float(r["preco"]),
                "imagem": r["imagem"],
            }
            for r in cur.fetchall()
        ]


def alternar_favorito(usuario_id: int, produto_id: int) -> Optional[bool]:
    prod = obter_produto(produto_id)
    if not prod:
        return None
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM favoritos WHERE usuario_id = ? AND produto_id = ?",
            (usuario_id, produto_id),
        )
        row = cur.fetchone()
        if row:
            cur.execute("DELETE FROM favoritos WHERE id = ?", (row["id"],))
            conn.commit()
            return False
        else:
            cur.execute(
                "INSERT INTO favoritos (usuario_id, produto_id) VALUES (?, ?)",
                (usuario_id, produto_id),
            )
            conn.commit()
            return True


# ---------------------------
# Pedidos
# ---------------------------

def criar_pedido(usuario_id: int, total: float, metodo_pagamento: str, status: str) -> int:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO pedidos (usuario_id, total, metodo_pagamento, status, criado_em) VALUES (?, ?, ?, ?, ?)",
            (usuario_id, float(total), metodo_pagamento, status, datetime.utcnow().isoformat() + "Z"),
        )
        conn.commit()
        return cur.lastrowid


def adicionar_item_pedido(pedido_id: int, produto_id: int, nome: str, preco: float, quantidade: int, tamanho: Optional[str]) -> None:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO pedido_itens (pedido_id, produto_id, nome, preco, tamanho, quantidade) VALUES (?, ?, ?, ?, ?, ?)",
            (pedido_id, produto_id, nome, float(preco), tamanho, int(quantidade)),
        )
        conn.commit()


def listar_pedidos(usuario_id: int) -> List[Dict[str, Any]]:
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY id DESC",
            (usuario_id,),
        )
        pedidos = [dict(r) for r in cur.fetchall()]
        for p in pedidos:
            cur.execute(
                "SELECT nome, preco, quantidade, tamanho FROM pedido_itens WHERE pedido_id = ?",
                (p["id"],),
            )
            p["itens"] = [
                {"nome": r["nome"], "preco": float(r["preco"]), "quantidade": int(r["quantidade"]), "tamanho": r["tamanho"]}
                for r in cur.fetchall()
            ]
        return pedidos


def decrementar_estoque(produto_id: int, tamanho: str, quantidade: int) -> bool:
    """Decrementa estoque do tamanho informado se houver saldo suficiente."""
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT estoque FROM produtos_tamanhos WHERE produto_id = ? AND tamanho = ?",
            (produto_id, tamanho),
        )
        row = cur.fetchone()
        if not row:
            return False
        atual = int(row[0])
        if atual < quantidade:
            return False
        novo = atual - quantidade
        cur.execute(
            "UPDATE produtos_tamanhos SET estoque = ? WHERE produto_id = ? AND tamanho = ?",
            (novo, produto_id, tamanho),
        )
        conn.commit()
        return True


# Executar inicialização quando arquivo é executado diretamente
if __name__ == "__main__":
    print("🚀 Inicializando banco de dados DYVA...")
    
    try:
        # Inicializar estrutura do banco
        inicializar_banco()
        print("✅ Estrutura do banco criada com sucesso!")
        
        # Criar dados iniciais (admin + produtos)
        criar_admin_e_produtos()
        print("✅ Dados iniciais criados com sucesso!")
        
        # Verificar resultado
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM produtos") 
        produtos = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Banco inicializado: {usuarios} usuários, {produtos} produtos")
        print("🎯 Banco pronto para uso!")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        print("🔧 Verifique se o arquivo dyva.db pode ser criado nesta pasta")
