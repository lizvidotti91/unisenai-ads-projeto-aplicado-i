import os
import sys

_RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, _RAIZ_PROJETO)

from .conexao import ConexaoBanco
from .tecnico_dao import TecnicoDAO
from .equipamento_dao import EquipamentoDAO
from .medicao_dao import MedicaoDAO

__all__ = ["ConexaoBanco", "TecnicoDAO", "EquipamentoDAO", "MedicaoDAO"]

CAMINHO_BANCO_PADRAO = os.path.join(_RAIZ_PROJETO, "metrologia.db")
