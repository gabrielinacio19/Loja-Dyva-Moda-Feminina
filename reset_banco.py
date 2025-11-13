# Script para resetar banco para apresentação
import os
import banco

def reset_para_apresentacao():
    """Reseta banco com dados limpos para apresentação"""
    
    # Remove banco atual se existir
    if os.path.exists('dyva.db'):
        os.remove('dyva.db')
        print("✅ Banco anterior removido")
    
    # Recria estrutura
    banco.inicializar_banco()
    print("✅ Estrutura do banco recriada")
    
    # Cria dados iniciais limpos
    banco.criar_admin_e_produtos()
    print("✅ Dados iniciais criados")
    
    print("\n🎬 BANCO PRONTO PARA APRESENTAÇÃO!")
    print("- Admin: admin@dyva.com / 123456")
    print("- Usuario teste: usuario@teste.com / senha123")  
    print("- 5 produtos cadastrados")
    print("- Nenhuma compra realizada")
    print("- Carrinho vazio")

if __name__ == "__main__":
    reset_para_apresentacao()