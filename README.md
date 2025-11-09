# 🛍️ DYVA - E-commerce de Moda Feminina

Sistema completo de e-commerce com frontend SPA, API REST Flask e banco SQLite.

## 🚀 Como Executar

### 1. Instalação
```powershell
pip install -r requirements.txt
```

### 2. Inicializar Banco de Dados
```powershell
python banco.py
```

### 3. Iniciar Backend
```powershell
python app.py
```
*Backend rodará em: http://localhost:5000*

### 4. Abrir Frontend
Abrir `site.html` no navegador

## 🎯 Funcionalidades Completas

### 👤 **Autenticação**
- Cadastro e login de usuários
- Autenticação por token (SHA-256)
- Perfil de administrador
- Logout seguro

### 🛒 **E-commerce**
- Catálogo de produtos com filtros
- Busca em tempo real
- Carrinho de compras
- Sistema de favoritos
- Histórico de pedidos
- Gestão de estoque

### 🎨 **Interface**
- Design responsivo
- Modo escuro/claro
- Single Page Application (SPA)
- Navegação intuitiva
- Feedback visual em tempo real

## 🔧 Arquitetura Técnica

### **Backend (Flask)**
- **18 endpoints REST API**
- Autenticação por token
- CORS configurado
- Validação de dados
- Tratamento de erros

### **Banco de Dados (SQLite)**
- **8 tabelas estruturadas:**
  - usuarios, produtos, produtos_tamanhos
  - carrinhos, favoritos, sessoes
  - pedidos, pedido_itens

### **Frontend (SPA)**
- HTML5 + CSS3 + JavaScript puro
- Comunicação assíncrona com API
- Interface responsiva
- Validação client-side

## 🧪 Testes Automatizados

### Executar Suite de Testes:
```powershell
python teste_completo.py
```
*Testa os principais fluxos do sistema*

### Interface de Testes:
Abrir `teste-integracao.html` no navegador

## 🔑 Credenciais de Teste

### Administrador:
- **Email:** admin@dyva.com
- **Senha:** 123456

### Usuário Comum:
- **Email:** usuario@teste.com  
- **Senha:** senha123

## � Endpoints da API

### Autenticação
- `POST /api/login` - Login
- `POST /api/registro` - Cadastro de usuário
- `GET /api/me` - Informações do usuário logado

### Produtos
- `GET /api/produtos` - Listar produtos
- `GET /api/produtos/<id>` - Produto específico
- `POST /api/produtos` - Criar produto (admin)
- `PUT /api/produtos/<id>` - Editar produto (admin)
- `DELETE /api/produtos/<id>` - Deletar produto (admin)

### Carrinho
- `GET /api/carrinho` - Ver carrinho
- `POST /api/carrinho/adicionar` - Adicionar item
- `POST /api/carrinho/remover` - Remover item
- `POST /api/carrinho/limpar` - Limpar carrinho

### Favoritos
- `GET /api/favoritos` - Listar favoritos
- `POST /api/favoritos/toggle` - Adicionar/remover favorito

### Pedidos
- `POST /api/pedidos/finalizar` - Finalizar pedido
- `GET /api/pedidos` - Histórico de pedidos

## 📁 Estrutura do Projeto

```
dyva/
├── app.py                          # Backend Flask com API REST
├── banco.py                        # Script de criação do banco
├── site.html                       # Frontend SPA completo
├── dyva.db                         # Banco SQLite com dados
├── requirements.txt                # Dependências Python
├── teste_completo.py               # Suite de testes automatizados
├── teste-integracao.html           # Interface de testes
├── explorar_banco.py               # Ferramenta de exploração do BD
├── visualizar_banco.py             # Monitor em tempo real do BD
├── simular_operacoes.py            # Simulador de operações
├── validacao_completa_backend.py   # Validação do backend
├── testar_banco.py                 # Testes unitários do banco
└── README.md                       # Documentação completa
```

## 🎓 Projeto Acadêmico

Sistema desenvolvido como projeto acadêmico demonstrando:
- Arquitetura full-stack
- API REST bem estruturada
- Frontend moderno responsivo
- Testes automatizados completos
- Banco de dados normalizado
