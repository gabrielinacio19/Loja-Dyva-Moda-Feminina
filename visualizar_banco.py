#!/usr/bin/env python3
"""
🔍 VISUALIZADOR DO BANCO DE DADOS DYVA
Mostra todas as tabelas e dados em tempo real
"""
import banco
from datetime import datetime

def mostrar_linha():
    print("=" * 60)

def visualizar_usuarios():
    print("👥 USUÁRIOS CADASTRADOS:")
    mostrar_linha()
    
    conn = banco.conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email, role FROM usuarios ORDER BY id")
    usuarios = cur.fetchall()
    conn.close()
    
    if not usuarios:
        print("   Nenhum usuário encontrado")
        return
    
    for user in usuarios:
        print(f"   ID: {user[0]} | Nome: {user[1]} | Email: {user[2]} | Tipo: {user[3]}")
    print()

def visualizar_produtos():
    print("📦 PRODUTOS NO CATÁLOGO:")
    mostrar_linha()
    
    produtos = banco.listar_produtos(ativos=True)
    
    if not produtos:
        print("   Nenhum produto encontrado")
        return
    
    for p in produtos:
        print(f"   ID: {p['id']} | {p['nome']} | R$ {p['preco']} | Cat: {p['categoria']}")
        
        # Mostrar tamanhos disponíveis
        conn = banco.conectar()
        cur = conn.cursor()
        cur.execute("SELECT tamanho, estoque FROM produtos_tamanhos WHERE produto_id = ? ORDER BY id", (p['id'],))
        tamanhos = cur.fetchall()
        conn.close()
        
        if tamanhos:
            tamanhos_str = ", ".join([f"{t[0]}({t[1]})" for t in tamanhos])
            print(f"      Tamanhos: {tamanhos_str}")
        print()

def visualizar_sessoes():
    print("🔐 SESSÕES ATIVAS:")
    mostrar_linha()
    
    conn = banco.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.token, u.nome, u.email, s.criado_em 
        FROM sessoes s 
        JOIN usuarios u ON s.usuario_id = u.id 
        ORDER BY s.criado_em DESC
    """)
    sessoes = cur.fetchall()
    conn.close()
    
    if not sessoes:
        print("   Nenhuma sessão ativa")
        return
    
    for sessao in sessoes:
        token_curto = sessao[0][:20] + "..."
        print(f"   Token: {token_curto} | User: {sessao[1]} ({sessao[2]}) | Criado: {sessao[3]}")
    print()

def visualizar_carrinho():
    print("🛒 ITENS NOS CARRINHOS:")
    mostrar_linha()
    
    conn = banco.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.usuario_id, u.nome, p.nome, c.quantidade, c.tamanho
        FROM carrinhos c
        JOIN usuarios u ON c.usuario_id = u.id
        JOIN produtos p ON c.produto_id = p.id
        ORDER BY c.usuario_id, p.nome
    """)
    itens = cur.fetchall()
    conn.close()
    
    if not itens:
        print("   Todos os carrinhos estão vazios")
        return
    
    usuario_atual = None
    for item in itens:
        if item[0] != usuario_atual:
            print(f"\n   👤 {item[1]} (ID: {item[0]}):")
            usuario_atual = item[0]
        
        tamanho_info = f" (Tamanho: {item[4]})" if item[4] else ""
        print(f"      • {item[2]} x{item[3]}{tamanho_info}")
    print()

def visualizar_pedidos():
    print("📋 PEDIDOS REALIZADOS:")
    mostrar_linha()
    
    conn = banco.conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, u.nome, p.total, p.status, p.criado_em
        FROM pedidos p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.criado_em DESC
        LIMIT 10
    """)
    pedidos = cur.fetchall()
    conn.close()
    
    if not pedidos:
        print("   Nenhum pedido encontrado")
        return
    
    for pedido in pedidos:
        print(f"   Pedido #{pedido[0]} | {pedido[1]} | R$ {pedido[2]} | {pedido[3]} | {pedido[4]}")
    print()

def mostrar_estatisticas():
    print("📊 ESTATÍSTICAS GERAIS:")
    mostrar_linha()
    
    conn = banco.conectar()
    cur = conn.cursor()
    
    # Contar usuários
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]
    
    # Contar produtos
    cur.execute("SELECT COUNT(*) FROM produtos WHERE ativo = 1")
    total_produtos = cur.fetchone()[0]
    
    # Contar sessões ativas
    cur.execute("SELECT COUNT(*) FROM sessoes")
    total_sessoes = cur.fetchone()[0]
    
    # Contar itens no carrinho
    cur.execute("SELECT COUNT(*) FROM carrinhos")
    total_carrinho = cur.fetchone()[0]
    
    # Contar pedidos
    cur.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cur.fetchone()[0]
    
    conn.close()
    
    print(f"   👥 Usuários cadastrados: {total_usuarios}")
    print(f"   📦 Produtos ativos: {total_produtos}")
    print(f"   🔐 Sessões ativas: {total_sessoes}")
    print(f"   🛒 Itens em carrinhos: {total_carrinho}")
    print(f"   📋 Pedidos realizados: {total_pedidos}")
    print()

def main():
    print("🔍 VISUALIZADOR DO BANCO DE DADOS DYVA")
    print(f"📅 Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    mostrar_linha()
    print()
    
    try:
        mostrar_estatisticas()
        visualizar_usuarios()
        visualizar_produtos()
        visualizar_sessoes()
        visualizar_carrinho()
        visualizar_pedidos()
        
        print("✅ Visualização concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")

if __name__ == "__main__":
    main()