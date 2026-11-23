"""
04_classes.py - Projeto Aplicado I (UniSENAI) - Schulz S.A.
AV 03 - MVP Parte 1: classes de dominio e conexao/persistencia SQL.

Este arquivo reune, em um unico ponto de importacao, tudo o que o roteiro pede:

  Classes de dominio (pasta classes/)
    - TecnicoSolicitante : profissional (metrologista, signatario ou solicitante)
    - Equipamento        : MMC ou instrumento de medicao
    - Medicao            : ensaio de calibracao, com validarStatus() (APROVADO/REPROVADO)

  Conexao e persistencia (pasta database/)
    - ConexaoBanco       : gerencia a conexao sqlite3, cria as tabelas e executa SQL
    - TecnicoDAO, EquipamentoDAO, MedicaoDAO : CRUD (INSERT, SELECT, UPDATE, DELETE)

Os scripts 05_main.py e exemplo_uso.py importam diretamente dos pacotes:
    from classes import TecnicoSolicitante, Equipamento, Medicao
    from database import ConexaoBanco, TecnicoDAO, EquipamentoDAO, MedicaoDAO
"""

from classes import TecnicoSolicitante, Equipamento, Medicao
from database import ConexaoBanco, TecnicoDAO, EquipamentoDAO, MedicaoDAO

__all__ = [
    "TecnicoSolicitante", "Equipamento", "Medicao",
    "ConexaoBanco", "TecnicoDAO", "EquipamentoDAO", "MedicaoDAO",
]
