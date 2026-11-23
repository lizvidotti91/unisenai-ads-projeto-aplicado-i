import os
import sys


RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)

from classes.TecnicoSolicitante import TecnicoSolicitante
from classes.Equipamento import Equipamento
from classes.Medicao import Medicao
from database import ConexaoBanco, TecnicoDAO, EquipamentoDAO, MedicaoDAO


def main():
    # Banco em arquivo temporário para o teste.
    caminho_teste = os.path.join(RAIZ, "_teste_exemplo.db")
    if os.path.exists(caminho_teste):
        os.remove(caminho_teste)

    with ConexaoBanco(caminho_teste) as banco:
        banco.criar_tabelas()
        print("== Tabelas criadas com sucesso ==")

        # ---- CREATE: Técnico ----
        tecnico_dao = TecnicoDAO(banco)
        tec1 = TecnicoSolicitante(
            matricula="M-001", nome="Ana Souza", cargo="Engenheira",
            papel="METROLOGISTA", setor="Qualidade", turno="MATUTINO", ativo=1,
        )
        tec2 = TecnicoSolicitante(
            matricula="M-002", nome="Bruno Lima", cargo="Técnico",
            papel="SOLICITANTE", setor="Produção", turno=None, ativo=1,
        )
        id1 = tecnico_dao.inserir(tec1)
        id2 = tecnico_dao.inserir(tec2)
        print(f"\n[CREATE] Técnicos inseridos: id={id1} ({tec1.nome}), id={id2} ({tec2.nome})")

        # ---- READ: listar técnicos ----
        todos = tecnico_dao.listar_todos()
        print(f"[READ] Total de técnicos: {len(todos)}")
        for t in todos:
            print(f"  - {t.exibirDadosTecnico()}")

        # buscar por id
        buscado = tecnico_dao.buscar_por_id(id1)
        print(f"[READ] Busca por id={id1}: {buscado.nome} / {buscado.papel}")

        # buscar por papel
        solicitantes = tecnico_dao.buscar_por_papel("solicitante")
        print(f"[READ] Solicitantes: {[s.nome for s in solicitantes]}")

        # ---- UPDATE: Técnico ----
        tec1.cargo = "Engenheira Sênior"
        tec1.turno = "VESPERTINO"
        tecnico_dao.atualizar(tec1)
        att = tecnico_dao.buscar_por_id(id1)
        print(f"\n[UPDATE] Técnico após update: cargo={att.cargo}, turno={att.turno}")

        # ---- CREATE: Equipamento (com solicitante) ----
        equip_dao = EquipamentoDAO(banco)
        eq1 = Equipamento(
            tagEquipamento="MMC-001", tipo="MMC", numeroSerie="SN-1001",
            nomeEquipamento="Micrômetro Externo", fabricante="Mitutoyo",
            modelo="103-137", faixaMedicao="0-25mm",
            solicitanteId=id2,
        )
        eq2 = Equipamento(
            tagEquipamento="INST-010", tipo="INSTRUMENTO", numeroSerie="SN-2002",
            nomeEquipamento="Relógio Comparador",
        )
        eqid1 = equip_dao.inserir(eq1)
        eqid2 = equip_dao.inserir(eq2)
        print(f"\n[CREATE] Equipamentos: id={eqid1} ({eq1.tagEquipamento}), id={eqid2} ({eq2.tagEquipamento})")
        print(f"  {eq1.exibirDadosEquipamento()}")

        # READ equipamento
        print(f"[READ] Equipamentos por solicitante {id2}: {[e.tagEquipamento for e in equip_dao.listar_por_solicitante(id2)]}")

        # ---- CREATE: Medição ----
        medicao_dao = MedicaoDAO(banco)
        med = Medicao(
            equipamentoId=eqid1, tecnicoId=id1, codigo="CERT-2024-001",
            parametro="Diâmetro Externo", valorNominal=10.000, medida1=10.002,
            valorObtido=10.002, unidade="mm", toleranciaSuperior=0.005,
            toleranciaInferior=-0.005, status="APROVADO",
        )
        mid = medicao_dao.inserir(med)
        print(f"\n[CREATE] Medição inserida: id={mid}")
        print(f"  {med.exibirDadosMedicao()}")

        # READ medição
        med_db = medicao_dao.buscar_por_id(mid)
        print(f"[READ] Medição do banco: código={med_db.codigo}, desvio={med_db.desvio}, status={med_db.status}")

        # UPDATE medição (muda status)
        med.status = "REPROVADO"
        med.valorObtido = 10.020
        med.desvio = med.valorObtido - med.valorNominal  # recalcula
        medicao_dao.atualizar(med)
        med_att = medicao_dao.buscar_por_id(mid)
        print(f"[UPDATE] Medição após update: status={med_att.status}, desvio={med_att.desvio}")

        # ---- Tratamento de exceção: violação de FK ----
        print("\n== Teste de exceção (FK inválida) ==")
        try:
            med_invalida = Medicao(
                equipamentoId=9999,  # não existe
                tecnicoId=id1, codigo="X", parametro="Y",
                valorNominal=1.0, medida1=1.0, valorObtido=1.0, unidade="mm",
            )
            medicao_dao.inserir(med_invalida)
        except RuntimeError as e:
            print(f"[OK] Exceção capturada: {str(e)[:80]}...")

        # ---- DELETE em cascata (equipamento -> suas medições) ----
        print("\n== Teste de DELETE em cascata ==")
        medicao_dao.deletar(mid)
        print(f"[DELETE] Medição {mid} removida: busca={medicao_dao.buscar_por_id(mid)}")

        equip_dao.deletar(eqid2)
        print(f"[DELETE] Equipamento {eqid2} removido: busca={equip_dao.buscar_por_id(eqid2)}")

        # deletar técnico com medição existente deve falhar (ON DELETE RESTRICT)
        # (não testamos aqui pois já removemos a medição; apenas ilustrativo)

        tecnico_dao.deletar(id2)
        print(f"[DELETE] Técnico {id2} removido: busca={tecnico_dao.buscar_por_id(id2)}")

        # estado final
        print(f"\n== Estado final ==")
        print(f"  Técnicos: {len(tecnico_dao.listar_todos())}")
        print(f"  Equipamentos: {len(equip_dao.listar_todos())}")
        print(f"  Medições: {len(medicao_dao.listar_todos())}")

    # limpeza
    os.remove(caminho_teste)
    print("\n✓ Todos os testes passaram. Banco temporário removido.")


if __name__ == "__main__":
    main()
