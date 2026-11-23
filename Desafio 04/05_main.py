"""
05_main.py - Projeto Aplicado I (UniSENAI) - Schulz S.A.
Ponto de entrada da Parte 01: inicializa o banco SQLite e chama o gerador.
"""

import importlib
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)

from database import ConexaoBanco

# Importacao dinamica pois o nome do modulo comeca com digito ("07_...")
gerador_certificado = importlib.import_module("07_gerador_certificado")

CAMINHO_BANCO = os.path.join(RAIZ, "metrologia_schulz.db")
CAMINHO_PLANILHA = os.path.join(RAIZ, "planilha_schulz.xlsx")


def main():
    # Garante um banco limpo para a demonstracao da Parte 01
    if os.path.exists(CAMINHO_BANCO):
        os.remove(CAMINHO_BANCO)

    try:
        with ConexaoBanco(CAMINHO_BANCO) as banco:
            print("=" * 100)
            print("1) CRIACAO DO BANCO DE DADOS")
            print("=" * 100)
            banco.criar_tabelas()
            print("[OK] Tabelas criadas no SQLite.\n")

            # Chama o 07_gerador_certificado para executar a ingestao e exibir o relatorio
            gerador_certificado.executar_ingestao_e_relatorio(banco, CAMINHO_PLANILHA)

            print("\nImportacao concluida com sucesso.")

    except (RuntimeError, ValueError, FileNotFoundError) as erro:
        print(f"\n[ERRO] Falha na execucao: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()