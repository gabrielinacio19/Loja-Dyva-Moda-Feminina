# 🛍️ DYVA - E-commerce de Moda Feminina

Sistema completo de e-commerce desenvolvido como projeto acadêmico de Metodologias Ágeis. Uma plataforma full-stack para loja virtual de roupas femininas com frontend responsivo, backend robusto e banco de dados integrado.

## 💡 Sobre o Projeto

O projeto **Dyva Moda Feminina** foi desenvolvido para digitalizar uma loja de moda que operava apenas via redes sociais, transformando-a em uma plataforma completa de e-commerce. O sistema oferece vitrine de produtos, carrinho de compras, cadastro de clientes, controle de estoque e sistema de pedidos.

### 🏗️ **Stack Tecnológica:**
- **Frontend:** HTML5, CSS3, JavaScript (SPA)
- **Backend:** Flask (Python) com API REST  
- **Banco de Dados:** SQLite
- **Autenticação:** JWT Token
- **Design:** Figma para prototipagem

### 🎨 **Design e Protótipos:**
- **Protótipo Figma:** [Ver Design Completo](https://www.figma.com/design/MVYsvlhxCL7uafokocM3uW/Projeto-Dyva?node-id=3-13&t=antHckkby9nflvr6-1)
- **Protótipos GitHub:** [Arquivos do Figma](https://github.com/gabrielinacio19/Loja-Dyva-Moda-Feminina/tree/main/prototipo-%20figma)

## 👥 Equipe de Desenvolvimento

**Yasmim Nicole** – Product Owner (PO): Representou a loja Dyva, definiu as prioridades do backlog e validou as funcionalidades do sistema, garantindo que o produto final atendesse às necessidades do cliente.

**Gabriel Coatti** – Scrum Master: Responsável por aplicar as metodologias ágeis, organizar as reuniões de acompanhamento e auxiliar a equipe na remoção de impedimentos durante o desenvolvimento do projeto.

**Kaio Martins** – Desenvolvedor Front-end: Responsável pela criação das interfaces do sistema, como o catálogo, o login e o carrinho de compras, além de garantir a responsividade e a boa experiência do usuário.

**Fabricio Lucas** – Desenvolvedor Back-end: Ficou responsável pela implementação da lógica do servidor, rotas e integração do back-end com o banco de dados, assegurando o funcionamento correto das funcionalidades.

**Sarah Vitória** – Desenvolvedora de Banco de Dados e Testes: Responsável pela modelagem e estruturação do banco de dados, criação das tabelas, consultas e apoio nos testes e validação do sistema.

**Gabriel Inácio** – Líder do Projeto e Designer de Interface: Atuou na coordenação geral do grupo, organizando as etapas de desenvolvimento, além de ser o criador do protótipo visual completo no Figma, definindo as telas, cores e elementos da interface da Dyva Moda Feminina.

## 🚀 Como Executar

### 1. Instalação
```bash
pip install -r requirements.txt
```

### 2. Inicializar Banco de Dados
```bash
python banco.py
```

### 3. Iniciar Backend
```bash
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

## 🗄️ Banco de Dados Organizado

O sistema vem configurado com **apenas 2 usuários pré-cadastrados** para demonstração:

### 🔑 **Credenciais de Acesso:**
- **👑 Admin:** `admin@dyva.com` / `123456` (acesso completo)
- **👤 Usuário:** `usuario@teste.com` / `senha123` (cliente)

### 📦 **Produtos Inclusos:**
- 6 produtos de moda feminina
- Com variações de tamanho (PP, P, M, G, GG)

### 🔄 **Reset do Banco:**
```bash
python reset_banco.py
```
*Restaura o banco para estado inicial limpo (ideal para demonstrações)*

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
dyva-ecommerce/
├── � prototipo- figma/         # Protótipos e designs do Figma
├── �📄 app.py                    # Backend Flask com API REST
├── 📄 banco.py                  # Sistema de banco de dados SQLite
├── 📄 site.html                 # Frontend SPA completo
├── 📄 dyva.db                   # Banco SQLite com dados
├── 📄 requirements.txt          # Dependências Python
├── 📄 reset_banco.py            # Script de reset do banco
├── 📄 .gitignore                # Configuração Git
└── 📄 README.md                 # Documentação do projeto
```

## 📚 Resumo Acadêmico

O projeto foi desenvolvido como parte da disciplina Metodologias Ágeis, aplicando práticas do Scrum (como Product Backlog, Daily Scrum, Sprint Review e Kanban). Durante o processo, foram criados e integrados os três pilares do sistema:
- **Frontend** (interface e usabilidade)
- **Backend** (regras de negócio e API)
- **Banco de Dados** (armazenamento e persistência de dados)

O resultado é uma aplicação funcional, organizada e moderna, que demonstra o uso das boas práticas de desenvolvimento ágil em um contexto real.

## 🎓 Projeto Acadêmico

Sistema desenvolvido como projeto acadêmico demonstrando:
- Arquitetura full-stack
- API REST bem estruturada  
- Frontend moderno responsivo
- Banco de dados normalizado
