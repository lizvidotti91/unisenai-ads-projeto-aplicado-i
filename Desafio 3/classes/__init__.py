"""
Pacote classes — classes de domínio do sistema de metrologia.

Permite importar de forma conveniente:

    from classes import TecnicoSolicitante, Equipamento, Medicao

em vez de:

    from classes.TecnicoSolicitante import TecnicoSolicitante
"""

from .TecnicoSolicitante import TecnicoSolicitante
from .Equipamento import Equipamento
from .Medicao import Medicao

__all__ = ["TecnicoSolicitante", "Equipamento", "Medicao"]