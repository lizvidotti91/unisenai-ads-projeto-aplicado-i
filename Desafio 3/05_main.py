"""
05_main.py - Projeto Aplicado I (UniSENAI) - Schulz S.A.
AV 03 - MVP Parte 1: script principal de demonstracao.

O que este script faz:
  1. Cria um banco SQLite limpo e as tabelas (via ConexaoBanco).
  2. Instancia objetos de teste (Tecnico, Equipamento, Medicao) e os grava no banco (DAOs).
  3. Valida cada medicao (APROVADO / REPROVADO / PENDENTE) pela tolerancia.
  4. Atualiza (UPDATE) uma medicao reprovada apos re-medicao.
  5. Faz uma consulta com JOIN entre as 3 tabelas.
  6. Exibe o Relatorio de Calibracao no terminal.

Como executar (na raiz do projeto, no VS Code):
    python 05_main.py

Todos os dados abaixo sao FICTICIOS, criados apenas para demonstrar o MVP.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)

from classes import TecnicoSolicitante, Equipamento, Medicao
from database import ConexaoBanco, TecnicoDAO, EquipamentoDAO, MedicaoDAO

# Banco exclusivo da demonstracao (recriado a cada execucao).
CAMINHO_BANCO_DEMO = os.path.join(RAIZ, "demo_mvp.db")

# Folga numerica para comparar numeros decimais (evita 0.0100000001 > 0.01).
EPS = 1e-9


# ---------------------------------------------------------------------------
# Utilidades de apresentacao
# ---------------------------------------------------------------------------
def titulo(texto: str):
    print("\n" + "=" * 100)
    print(texto)
    print("=" * 100)


# ---------------------------------------------------------------------------
# Validacao metrologica
# ---------------------------------------------------------------------------
def validar_status(medicao: Medicao) -> str:
    """Define o status da medicao pela tolerancia.

    Se a classe Medicao ja possuir o metodo validarStatus(), ele e usado.
    Caso contrario, aplica a mesma regra aqui (tolerancia = desvio permitido
    em relacao ao nominal; aceita tolerancia unilateral):

        desvio > tolerancia superior  -> REPROVADO
        desvio < tolerancia inferior  -> REPROVADO
        dentro dos limites            -> APROVADO
        sem nenhuma tolerancia        -> PENDENTE
    """
    if hasattr(medicao, "validarStatus"):
        return medicao.validarStatus()

    sup, inf = medicao.toleranciaSuperior, medicao.toleranciaInferior
    if sup is None and inf is None:
        medicao.status = "PENDENTE"
    else:
        acima = sup is not None and medicao.desvio > sup + EPS
        abaixo = inf is not None and medicao.desvio < inf - EPS
        medicao.status = "REPROVADO" if (acima or abaixo) else "APROVADO"
    return medicao.status


# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------
def cadastrar_tecnicos(dao: TecnicoDAO) -> dict:
    tecnicos = {
        "metrologista": TecnicoSolicitante(
            matricula="M-001", nome="Carlos Metrologista", cargo="Metrologista",
            papel="METROLOGISTA", setor="Laboratorio de Metrologia", turno="MATUTINO"),
        "signatario": TecnicoSolicitante(
            matricula="M-002", nome="Marina Signataria", cargo="Responsavel Tecnica",
            papel="SIGNATARIO", setor="Laboratorio de Metrologia", turno="MATUTINO"),
        "solicitante": TecnicoSolicitante(
            matricula="P-101", nome="Paulo Producao", cargo="Supervisor",
            papel="SOLICITANTE", setor="Producao", turno="VESPERTINO"),
    }
    for t in tecnicos.values():
        dao.inserir(t)
    print(f"[INSERT] {len(tecnicos)} tecnicos cadastrados.")
    return tecnicos


def cadastrar_equipamentos(dao: EquipamentoDAO, tecnicos: dict) -> dict:
    equipamentos = {
        # Padrao interno da Schulz usado nas medicoes (piloto do projeto).
        "mmc": Equipamento(
            tagEquipamento="MMC-500.011", tipo="MMC", numeroSerie="502390",
            nomeEquipamento="Maquina de Medicao por Coordenadas", fabricante="Zeiss",
            modelo="Contura G2", faixaMedicao="700x1000x600 mm",
            rastreabilidade="Cert. RBC (dado ficticio)"),
        # Instrumentos de clientes internos calibrados na MMC.
        "calibre": Equipamento(
            tagEquipamento="PA-0231", tipo="INSTRUMENTO", numeroSerie="PA-98001",
            nomeEquipamento="Calibre de Limites", fabricante="Mitutoyo",
            partNo="PN-7782", solicitanteId=tecnicos["solicitante"].idTecnico),
        "gabarito": Equipamento(
            tagEquipamento="GB-0107", tipo="INSTRUMENTO", numeroSerie="GB-44102",
            nomeEquipamento="Gabarito de Posicao", fabricante=None,
            drawningNo="DES-3345", solicitanteId=tecnicos["solicitante"].idTecnico),
    }
    for e in equipamentos.values():
        dao.inserir(e)
    print(f"[INSERT] {len(equipamentos)} equipamentos cadastrados.")
    return equipamentos


def montar_medicoes(tecnicos: dict, equipamentos: dict) -> list:
    """Cria as medicoes de teste. Cobre APROVADO, REPROVADO (acima e abaixo),
    tolerancia unilateral e caso sem tolerancia (PENDENTE)."""
    tec = tecnicos["metrologista"].idTecnico
    mmc = equipamentos["mmc"].idEquipamento
    calibre = equipamentos["calibre"].idEquipamento
    gabarito = equipamentos["gabarito"].idEquipamento

    comum = dict(tecnicoId=tec, padraoId=mmc, planoMedicao="PLANO-CAL-01")

    return [
        # --- Calibre de Limites -------------------------------------------
        Medicao(equipamentoId=calibre, codigo="C01", parametro="Diametro 1",
                valorNominal=10.000, medida1=10.002, medida2=10.002, valorObtido=10.002,
                toleranciaSuperior=0.005, toleranciaInferior=-0.005,
                dtHoraMedicao="2026-11-02 08:10:00", **comum),
        Medicao(equipamentoId=calibre, codigo="C02", parametro="Diametro 2",
                valorNominal=25.000, medida1=25.012, medida2=25.014, valorObtido=25.013,
                toleranciaSuperior=0.010, toleranciaInferior=-0.010,
                dtHoraMedicao="2026-11-02 08:11:00", **comum),
        Medicao(equipamentoId=calibre, codigo="C03", parametro="Comprimento",
                valorNominal=50.000, medida1=49.989, medida2=49.991, valorObtido=49.990,
                toleranciaSuperior=0.010, toleranciaInferior=-0.005,
                dtHoraMedicao="2026-11-02 08:12:00", **comum),
        # --- Gabarito de Posicao ------------------------------------------
        Medicao(equipamentoId=gabarito, codigo="G01", parametro="Planicidade",
                valorNominal=0.000, medida1=0.003, medida2=0.004, valorObtido=0.004,
                toleranciaSuperior=0.010, toleranciaInferior=None,   # unilateral
                eixoReferencia="Z", dtHoraMedicao="2026-11-02 09:30:00", **comum),
        Medicao(equipamentoId=gabarito, codigo="G02", parametro="Posicao X",
                valorNominal=100.000, medida1=100.020, medida2=100.022, valorObtido=100.021,
                toleranciaSuperior=0.015, toleranciaInferior=-0.015, eixoReferencia="X",
                dtHoraMedicao="2026-11-02 09:31:00", **comum),
        Medicao(equipamentoId=gabarito, codigo="G03", parametro="Angulo",
                valorNominal=90.000, medida1=90.010, medida2=90.010, valorObtido=90.010,
                unidade="graus",                                     # sem tolerancia
                dtHoraMedicao="2026-11-02 09:32:00", **comum),
    ]


# ---------------------------------------------------------------------------
# Relatorio (consulta com JOIN entre as 3 tabelas)
# ---------------------------------------------------------------------------
SQL_RELATORIO = """
SELECT  m.idMedicao,
        m.dtHoramedicao   AS data_hora,
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


def fmt_tol(inf, sup) -> str:
    i = "-" if inf is None else f"{inf:+.3f}"
    s = "-" if sup is None else f"{sup:+.3f}"
    return f"{i} / {s}"


def exibir_relatorio(banco: ConexaoBanco):
    linhas = banco.consultar(SQL_RELATORIO)

    titulo("RELATORIO DE CALIBRACAO - SCHULZ S.A. (dados de teste)")
    if not linhas:
        print("Nenhuma medicao encontrada.")
        return

    tag_atual = None
    for r in linhas:
        if r["tag"] != tag_atual:
            tag_atual = r["tag"]
            print(f"\nEquipamento: {r['tag']} - {r['equipamento']}")
            print(f"  Solicitante: {r['solicitante'] or 'Interno (Schulz)'} | "
                  f"Padrao utilizado: {r['padrao'] or '-'} | Metrologista: {r['metrologista']}")
            print(f"  {'Cod':<4} {'Parametro':<13} {'Un':<5} {'Nominal':>9} {'Obtido':>9} "
                  f"{'Desvio':>9} {'Tol (inf / sup)':>17}  Status")
            print("  " + "-" * 82)
        print(f"  {r['codigo']:<4} {r['parametro']:<13} {r['unidade']:<5} "
              f"{r['valorNominal']:>9.3f} {r['valorObtido']:>9.3f} {r['desvio']:>+9.3f} "
              f"{fmt_tol(r['toleranciaInferior'], r['toleranciaSuperior']):>17}  {r['status']}")

    total = len(linhas)
    cont = {"APROVADO": 0, "REPROVADO": 0, "PENDENTE": 0}
    for r in linhas:
        cont[r["status"]] += 1
    print("\n" + "-" * 100)
    print(f"RESUMO: {total} medicoes | {cont['APROVADO']} aprovadas | "
          f"{cont['REPROVADO']} reprovadas | {cont['PENDENTE']} pendentes (sem tolerancia)")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    if os.path.exists(CAMINHO_BANCO_DEMO):
        os.remove(CAMINHO_BANCO_DEMO)

    try:
        with ConexaoBanco(CAMINHO_BANCO_DEMO) as banco:
            titulo("1) CRIACAO DO BANCO E INSERCAO DOS DADOS DE TESTE")
            banco.criar_tabelas()
            print("[OK] Tabelas criadas.")

            tecnico_dao = TecnicoDAO(banco)
            equipamento_dao = EquipamentoDAO(banco)
            medicao_dao = MedicaoDAO(banco)

            tecnicos = cadastrar_tecnicos(tecnico_dao)
            equipamentos = cadastrar_equipamentos(equipamento_dao, tecnicos)

            titulo("2) VALIDACAO METROLOGICA (APROVADO / REPROVADO)")
            medicoes = montar_medicoes(tecnicos, equipamentos)
            for m in medicoes:
                validar_status(m)
                print(f"  {m.codigo} {m.parametro:<13} desvio {m.desvio:+.3f} "
                      f"tol [{fmt_tol(m.toleranciaInferior, m.toleranciaSuperior)}] -> {m.status}")
                medicao_dao.inserir(m)
            print(f"[INSERT] {len(medicoes)} medicoes gravadas.")

            titulo("3) UPDATE: RE-MEDICAO DE UMA CARACTERISTICA REPROVADA")
            reprovada = next(m for m in medicoes if m.codigo == "C02")
            print(f"  Antes : {reprovada.codigo} obtido {reprovada.valorObtido:.3f} -> {reprovada.status}")
            reprovada.medida1, reprovada.medida2, reprovada.valorObtido = 25.007, 25.009, 25.008
            validar_status(reprovada)          # recalcula desvio e status
            medicao_dao.atualizar(reprovada)   # UPDATE no banco
            do_banco = medicao_dao.buscar_por_id(reprovada.idMedicao)
            print(f"  Depois: {do_banco.codigo} obtido {do_banco.valorObtido:.3f} -> {do_banco.status} (lido do banco)")

            titulo("4) TRATAMENTO DE ERRO SQL (chave estrangeira invalida)")
            invalida = Medicao(equipamentoId=999, tecnicoId=tecnicos["metrologista"].idTecnico,
                               codigo="X99", parametro="Teste", valorNominal=1.0,
                               medida1=1.0, valorObtido=1.0)
            try:
                medicao_dao.inserir(invalida)
            except RuntimeError as erro:
                print("[OK] Erro capturado e banco preservado:")
                print("    " + str(erro).splitlines()[0])

            exibir_relatorio(banco)

    except (RuntimeError, ValueError) as erro:
        print(f"\n[ERRO] A demonstracao foi interrompida: {erro}")
        sys.exit(1)
    finally:
        # O arquivo demo pode ser apagado; o relatorio ja foi exibido.
        pass

    print("\nDemonstracao concluida com sucesso.")


if __name__ == "__main__":
    main()
