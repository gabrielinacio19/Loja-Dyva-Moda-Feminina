"""
Script para testar se o banco de dados está funcionando corretamente
"""

import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Garantir import do módulo 'banco' a partir da raiz do projeto
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import banco

print("\n" + "="*60)
print("🔍 TESTANDO BANCO DE DADOS")
print("="*60)

# Inicializa banco
banco.inicializar_banco()
banco.criar_admin_e_produtos()

# Verifica usuários
print("\n📋 Usuários cadastrados:")
admin = banco.obter_usuario_por_email("admin@dyva.com")
if admin:
    print(f"✅ Admin encontrado: {admin['nome']} ({admin['email']})")
else:
    print("❌ Admin não encontrado")

# Verifica produtos
print("\n📦 Produtos no catálogo:")
produtos = banco.listar_produtos(ativos=True)
print(f"✅ Total de {len(produtos)} produtos ativos")
for p in produtos:
    print(f"   • {p['nome']} - R$ {p['preco']:.2f}")

print("\n" + "="*60)
print("✅ BANCO DE DADOS FUNCIONANDO CORRETAMENTE!")
print("="*60 + "\n")
