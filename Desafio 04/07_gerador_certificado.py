"""
07_gerador_certificado.py - Projeto Aplicado I (UniSENAI) - Schulz S.A.
Aciona o IngestaoService e exibe o relatorio consolidado de calibracao a partir do banco de dados.
"""

from database import ConexaoBanco
from service import IngestaoService

SQL_RELATORIO = """
SELECT  m.idMedicao,
        m.dtHoraMedicao   AS data_hora,
        e.tagEquipamento  AS tag,
        e.nomeEquipamento AS equipamento,
        p.tagEquipamento  AS padrao_tag,
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
WHERE e.tagEquipamento = ?
ORDER BY m.codigo
"""


def _fmt_tol(inf, sup) -> str:
    i = "-" if inf is None else f"{inf:+.4f}"
    s = "-" if sup is None else f"{sup:+.4f}"
    return f"{i} / {s}"


def executar_ingestao_e_relatorio(banco: ConexaoBanco, caminho_planilha: str) -> dict:
    """
    Executa a ingestao via Service e imprime o relatorio consolidado no terminal.
    Retorna o resumo da operacao de ingestao.
    """
    print("=" * 100)
    print("2) IMPORTACAO DA PLANILHA EXCEL (IngestaoService)")
    print("=" * 100)

    ingestao = IngestaoService(banco)
    resumo = ingestao.importar_planilha(caminho_planilha)

    tag = resumo["equipamento_tag"]
    print(f"[OK] Equipamento importado (TAG): {tag}")
    print(f"[OK] Registros de medicao salvos: {resumo['registros_salvos']}")

    if resumo["alertas"]:
        print("\n[ALERTAS DE HIGIENIZACAO]:")
        for alerta in resumo["alertas"]:
            print(f"- {alerta}")

    # Consulta os dados validados no banco para exibicao
    linhas = banco.consultar(SQL_RELATORIO, (tag,))
    if not linhas:
        return resumo

    cab = linhas[0]
    total = len(linhas)
    aprovadas = sum(1 for r in linhas if r["status"] == "APROVADO")
    reprovadas = sum(1 for r in linhas if r["status"] == "REPROVADO")
    pendentes = sum(1 for r in linhas if r["status"] == "PENDENTE")

    print("\n" + "=" * 100)
    print("RELATORIO DE CALIBRACAO - SCHULZ S.A. (Dados Importados da Planilha)")
    print("=" * 100)
    print(f"\nEquipamento: {cab['tag']} - {cab['equipamento']}")
    print(
        f"  Solicitante: {cab['solicitante'] or '-'} | "
        f"Padrao utilizado: {cab['padrao_tag'] or '-'} | "
        f"Metrologista: {cab['metrologista']}"
    )
    print(
        f"  {'Cod':<4} {'Parametro':<25} {'Un':<4} {'Nominal':>10} "
        f"{'Obtido':>10} {'Desvio':>10} {'Tol (inf / sup)':>19}  Status"
    )
    print("  " + "-" * 98)

    for r in linhas:
        print(
            f"  {r['codigo']:<4} {r['parametro']:<25} {r['unidade']:<4} "
            f"{r['valorNominal']:>10.4f} {r['valorObtido']:>10.4f} {r['desvio']:>+10.4f} "
            f"{_fmt_tol(r['toleranciaInferior'], r['toleranciaSuperior']):>19}  {r['status']}"
        )

    print("\n" + "-" * 100)
    print(
        f"RESUMO: {total} medicoes | {aprovadas} aprovadas | "
        f"{reprovadas} reprovadas | {pendentes} pendentes"
    )

    return resumo