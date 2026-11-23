"""
05_main.py - Projeto Aplicado I (UniSENAI) - Schulz S.A.
Demonstracao da Camada Service (Ingestao ETL da Planilha Schulz).

O que este script faz:
1. Cria um banco SQLite limpo e as tabelas (via ConexaoBanco).
2. Executa o IngestaoService para ler o Excel (.xlsx), higienizar e salvar no banco.
3. Exibe o Relatorio de Calibracao consolidado no terminal.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)

from database import ConexaoBanco
from service import IngestaoService

# Banco exclusivo da demonstracao (recriado a cada execucao)
CAMINHO_BANCO_DEMO = os.path.join(RAIZ, "demo_schulz.db")

# Caminho da planilha Excel real da Schulz (coloque na mesma pasta ou ajuste o nome)
CAMINHO_PLANILHA = os.path.join(RAIZ, "planilha_schulz.xlsx")


def titulo(texto: str):
    print("\n" + "=" * 100)
    print(texto)
    print("=" * 100)


def fmt_tol(inf, sup) -> str:
    i = "-" if inf is None else f"{inf:+.4f}"
    s = "-" if sup is None else f"{sup:+.4f}"
    return f"{i} / {s}"


SQL_RELATORIO = """
SELECT  m.idMedicao,
        m.dtHoraMedicao   AS data_hora,
        e.tagEquipamento  AS tag,
        e.nomeEquipamento AS equipamento,
        p.tagEquipamento  AS padrao,
        t.nome            AS metrologista,
        s.nome            AS solicitante,
        m.codigo, m.parametro, m.unidade,
        m.valorNominal, m.valorObtido, m.desvio,
        m.toleranciaInferior, m.toleranciaSuperior,
        m.status
FROM medicoes m
JOIN equipamentos e       ON e.idEquipamento = m.equipamentoId
JOIN tecnicos     t       ON t.idTecnico     = m.tecnicoId
LEFT JOIN equipamentos p  ON p.idEquipamento = m.padraoId
LEFT JOIN tecnicos     s  ON s.idTecnico     = e.solicitanteId
ORDER BY e.tagEquipamento, m.codigo
"""


def exibir_relatorio(banco: ConexaoBanco):
    linhas = banco.consultar(SQL_RELATORIO)

    titulo("RELATORIO DE CALIBRACAO - SCHULZ S.A. (Dados Importados da Planilha)")
    if not linhas:
        print("Nenhuma medicao encontrada no banco.")
        return

    tag_atual = None
    for r in linhas:
        if r["tag"] != tag_atual:
            tag_atual = r["tag"]
            print(f"\nEquipamento: {r['tag']} - {r['equipamento']}")
            print(f"  Solicitante: {r['solicitante'] or 'Interno (Schulz)'} | "
                  f"Padrao utilizado: {r['padrao'] or '-'} | Metrologista: {r['metrologista']}")
            print(f"  {'Cod':<4} {'Parametro':<25} {'Un':<4} {'Nominal':>10} {'Obtido':>10} "
                  f"{'Desvio':>10} {'Tol (inf / sup)':>19}  Status")
            print("  " + "-" * 98)
        print(f"  {r['codigo']:<4} {r['parametro']:<25} {r['unidade']:<4} "
              f"{r['valorNominal']:>10.4f} {r['valorObtido']:>10.4f} {r['desvio']:>+10.4f} "
              f"{fmt_tol(r['toleranciaInferior'], r['toleranciaSuperior']):>19}  {r['status']}")

    total = len(linhas)
    cont = {"APROVADO": 0, "REPROVADO": 0, "PENDENTE": 0}
    for r in linhas:
        cont[r["status"]] += 1
    print("\n" + "-" * 100)
    print(f"RESUMO: {total} medicoes | {cont['APROVADO']} aprovadas | "
          f"{cont['REPROVADO']} reprovadas | {cont['PENDENTE']} pendentes")


def main():
    if os.path.exists(CAMINHO_BANCO_DEMO):
        os.remove(CAMINHO_BANCO_DEMO)

    try:
        with ConexaoBanco(CAMINHO_BANCO_DEMO) as banco:
            titulo("1) CRIACAO DO BANCO DE DADOS")
            banco.criar_tabelas()
            print("[OK] Tabelas criadas no SQLite.")

            titulo("2) IMPORTACAO DA PLANILHA EXCEL (IngestaoService)")
            ingestao = IngestaoService(banco)
            resumo = ingestao.importar_planilha(CAMINHO_PLANILHA)

            print(f"[OK] Equipamento importado (TAG): {resumo['equipamento_tag']}")
            print(f"[OK] Registros de medicao salvos: {resumo['registros_salvos']}")

            if resumo["alertas"]:
                print("\n[ALERTAS DE HIGIENIZACAO]:")
                for a in resumo["alertas"]:
                    print(f"  - {a}")

            if resumo["erros"]:
                print("\n[LINHAS IGNORADAS / ERROS]:")
                for e in resumo["erros"]:
                    print(f"  - {e}")

            exibir_relatorio(banco)

    except (RuntimeError, ValueError, FileNotFoundError) as erro:
        print(f"\n[ERRO] A importacao foi interrompida: {erro}")
        sys.exit(1)

    print("\nImportacao concluida com sucesso.")


if __name__ == "__main__":
    main()