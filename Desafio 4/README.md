# Sistema de Ingestão e Validação Metrológica — Schulz S.A.

README PARCIAL. INSTRUCOES PARA EXECUCAO DOS DADOS DE TESTE DA PARTE 01 DO ROTEIRO. ALTERAR O README PARA AS VERSOES FINAIS

## Pré-requisitos
* **Python 3.10** ou superior
* Biblioteca **`openpyxl`** (leitura de planilhas Excel `.xlsx`)

## Como preparar o ambiente e executar

### No Windows (PowerShell ou CMD)
1. Abra o terminal na pasta `Desafio 04`.
2. Instale a dependência do Excel:
   ```powershell
   pip install openpyxl
3. Execute o script principal
    ``powershell
    python 05_main.py

### No Linux (Ubuntu/ Debian)
1. Abra o terminal na pasta `Desafio 04`.
2. Instale a dependência do Excel:
   ```powershell
   sudo apt install -y python3-openpyxl
3. Execute o script principal
    ``powershell
    python3 05_main.py

(Nota: A cada execução do 05_main.py, o banco de demonstração demo_schulz.db é recriado do zero, os dados da planilha planilha_schulz.xlsx são importados e o relatório consolidado é exibido no terminal.)