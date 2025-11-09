#!/usr/bin/env python3
"""
🔍 EXPLORADOR DE ESTRUTURA DO BANCO DYVA
Mostra todas as tabelas e sua estrutura
"""
import sqlite3
import os

ARQUIVO_DB = os.path.join(os.path.dirname(__file__), "dyva.db")

def explorar_estrutura():
    print("🔍 EXPLORADOR DE ESTRUTURA DO BANCO DYVA")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(ARQUIVO_DB)
        cur = conn.cursor()
        
        # Listar todas as tabelas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cur.fetchall()
        
        print(f"📊 BANCO: {ARQUIVO_DB}")
        print(f"📋 TABELAS ENCONTRADAS: {len(tabelas)}")
        print()
        
        for i, (nome_tabela,) in enumerate(tabelas, 1):
            print(f"{i}. 📁 TABELA: {nome_tabela}")
            print("-" * 40)
            
            # Mostrar estrutura da tabela
            cur.execute(f"PRAGMA table_info({nome_tabela})")
            colunas = cur.fetchall()
            
            print("   COLUNAS:")
            for col in colunas:
                tipo = col[2]
                pk = " (PK)" if col[5] else ""
                notnull = " NOT NULL" if col[3] else ""
                print(f"     • {col[1]} - {tipo}{pk}{notnull}")
            
            # Contar registros
            cur.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            total = cur.fetchone()[0]
            print(f"   📊 REGISTROS: {total}")
            
            # Mostrar alguns dados de exemplo (máximo 3)
            if total > 0:
                cur.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
                exemplos = cur.fetchall()
                print("   📄 DADOS DE EXEMPLO:")
                for exemplo in exemplos:
                    print(f"     {exemplo}")
            
            print()
        
        conn.close()
        print("✅ Exploração concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    explorar_estrutura()