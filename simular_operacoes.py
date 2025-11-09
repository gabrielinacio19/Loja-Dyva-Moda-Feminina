#!/usr/bin/env python3
"""
🧪 SIMULADOR DE OPERAÇÕES - VER DADOS CHEGANDO NO BANCO
Simula várias operações e mostra como os dados são inseridos
"""
import requests
import time
import json
from datetime import datetime

API_URL = "http://127.0.0.1:5000/api"

def print_separator(title):
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def visualizar_banco_antes_depois(operacao):
    print(f"\n📊 BANCO ANTES DA OPERAÇÃO: {operacao}")
    print("-" * 40)
    
    # Executar o visualizador
    import subprocess
    try:
        result = subprocess.run(["python", "visualizar_banco.py"], 
                              capture_output=True, text=True, cwd=".")
        # Mostrar apenas estatísticas
        lines = result.stdout.split('\n')
        for line in lines[4:10]:  # Pegar só as estatísticas
            if line.strip():
                print(line)
    except:
        print("   Erro ao visualizar banco")

def simular_registro_usuario():
    print_separator("SIMULANDO REGISTRO DE NOVO USUÁRIO")
    
    # Mostrar banco antes
    visualizar_banco_antes_depois("Registro")
    
    email_teste = f"novo_usuario_{int(time.time())}@dyva.com"
    dados = {
        "nome": "Novo Usuario Teste",
        "email": email_teste,
        "senha": "123456"
    }
    
    print(f"\n🔄 ENVIANDO DADOS PARA: POST {API_URL}/registro")
    print(f"📤 DADOS: {json.dumps(dados, indent=2)}")
    
    try:
        response = requests.post(f"{API_URL}/registro", json=dados)
        print(f"📥 RESPOSTA: {response.status_code}")
        print(f"📝 CONTEÚDO: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Usuário registrado com sucesso!")
            
            print(f"\n📊 BANCO DEPOIS DA OPERAÇÃO:")
            print("-" * 40)
            time.sleep(1)  # Aguardar um pouco
            visualizar_banco_antes_depois("Pós-registro")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def simular_login_e_carrinho():
    print_separator("SIMULANDO LOGIN E ADIÇÃO AO CARRINHO")
    
    # Login primeiro
    dados_login = {
        "email": "admin@dyva.com",
        "senha": "123456"
    }
    
    print(f"\n🔄 FAZENDO LOGIN: POST {API_URL}/login")
    print(f"📤 DADOS: {json.dumps(dados_login, indent=2)}")
    
    try:
        response = requests.post(f"{API_URL}/login", json=dados_login)
        if response.status_code == 200:
            token = response.json()["token"]
            print(f"✅ Login realizado! Token: {token[:20]}...")
            
            # Adicionar ao carrinho
            headers = {"Authorization": f"Bearer {token}"}
            dados_carrinho = {
                "produto_id": 1,
                "tamanho": "M",
                "quantidade": 2
            }
            
            print(f"\n🔄 ADICIONANDO AO CARRINHO: POST {API_URL}/carrinho")
            print(f"📤 DADOS: {json.dumps(dados_carrinho, indent=2)}")
            print(f"🔑 HEADER: Authorization: Bearer {token[:20]}...")
            
            response2 = requests.post(f"{API_URL}/carrinho", json=dados_carrinho, headers=headers)
            print(f"📥 RESPOSTA: {response2.status_code}")
            
            if response2.status_code == 200:
                print("✅ Item adicionado ao carrinho!")
                
                # Ver carrinho
                print(f"\n🔄 CONSULTANDO CARRINHO: GET {API_URL}/carrinho")
                response3 = requests.get(f"{API_URL}/carrinho", headers=headers)
                if response3.status_code == 200:
                    carrinho = response3.json()
                    print(f"📦 CARRINHO ATUAL: {len(carrinho['itens'])} itens")
                    for item in carrinho['itens']:
                        print(f"   • {item['nome']} (Tamanho: {item['tamanho']}) x{item['quantidade']}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def simular_criacao_produto():
    print_separator("SIMULANDO CRIAÇÃO DE PRODUTO (ADMIN)")
    
    # Login como admin
    dados_login = {"email": "admin@dyva.com", "senha": "123456"}
    
    try:
        response = requests.post(f"{API_URL}/login", json=dados_login)
        if response.status_code == 200:
            token = response.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Criar produto
            produto_teste = {
                "nome": f"Produto Teste {int(time.time())}",
                "categoria": "Teste",
                "preco": 99.99,
                "imagem": "https://via.placeholder.com/300x300?text=Teste",
                "descricao": "Produto criado para demonstração"
            }
            
            print(f"\n🔄 CRIANDO PRODUTO: POST {API_URL}/admin/produtos")
            print(f"📤 DADOS: {json.dumps(produto_teste, indent=2)}")
            
            response2 = requests.post(f"{API_URL}/admin/produtos", 
                                    json=produto_teste, headers=headers)
            print(f"📥 RESPOSTA: {response2.status_code}")
            
            if response2.status_code == 201:
                produto_criado = response2.json()
                print(f"✅ Produto criado! ID: {produto_criado['id']}")
                print(f"📝 DADOS: {produto_criado}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    print("🧪 SIMULADOR DE OPERAÇÕES DO BANCO DYVA")
    print(f"🕐 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("\n⚠️  CERTIFIQUE-SE DE QUE O BACKEND ESTÁ RODANDO!")
    print("   Comando: python app.py")
    
    # Testar conexão
    try:
        response = requests.get(f"{API_URL}/produtos", timeout=3)
        if response.status_code == 200:
            print("✅ Backend está online!")
        else:
            print("❌ Backend não responde corretamente")
            return
    except:
        print("❌ Backend não está acessível")
        print("   Execute: python app.py")
        return
    
    # Executar simulações
    simular_registro_usuario()
    time.sleep(2)
    
    simular_login_e_carrinho()
    time.sleep(2)
    
    simular_criacao_produto()
    
    print_separator("SIMULAÇÃO CONCLUÍDA")
    print("🎉 Agora você viu como as informações chegam no banco!")
    print("💡 Para monitorar em tempo real, execute:")
    print("   python visualizar_banco.py")

if __name__ == "__main__":
    main()