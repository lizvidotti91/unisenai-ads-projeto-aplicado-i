# Estrutura do Banco de Dados Relacional — Projeto Schulz S.A.

## 1. Contexto Operacional e Objetivo
O objetivo deste trabalho é modernizar a emissão de certificados de calibração da Schulz S.A., migrando o processo manual, com utilização de planilhas eletrônicas, para um processo automatizado, de forma a: eliminar erros manuais de digitação, corrigir falhas nas fórmulas de cálculo hoje usadas nas planilhas, reunir os registros metrológicos em um único lugar e liberar os técnicos metrologistas de tarefas repetitivas que hoje consomem boa parte do tempo do laboratório.

## 2. Modelagem de Dados
A modelagem física em SQLite foi dividida em **7 entidades relacionais**, garantindo a separação clara de responsabilidades:

1. **`fornecedor_setor`:**
   - Cadastra os setores solicitantes e fornecedores de serviços/equipamentos da Schulz S.A., vinculando siglas operacionais e responsáveis pelo cadastro.
2. **`instrumento`:**
   - Armazena os dados cadastrais dos dispositivos de controle e medição (TAG, número de série, fabricante, número de desenho técnico `drawing_no` e código de peça `part_no`), ligando-se ao setor proprietário via `fk_fornecedor_id`.
3. **`metrologista`:**
   - Registra os técnicos habilitados para realizar as inspeções no laboratório, contendo matrícula, nome e turno de trabalho com validação de domínio (`CHECK`).
4. **`maquina_mmc`:**
   - Cadastra os equipamentos de medição por coordenadas (código MMC), os programas de medição executados (`measurement_plan`) e o horário das leituras.
5. **`certificado_calibracao`:**
   - Entidade centralizadora dos eventos de calibração. Consolida o número do certificado, a data do ensaio e o parecer de conformidade, conectando o metrologista (`fk_metrologista_id`), o instrumento (`fk_instrumento_id`) e a máquina MMC (`fk_mmc_id`).
6. **`medicao_caracteristica`:**
   - Armazena cada parâmetro dimensional medido (planicidade, diâmetro, etc.), registrando dimensão nominal, tolerâncias superior/inferior, valor lido e desvio apurado, vinculando-se ao certificado correspondente (`fk_certificado_id`).
7. **`incerteza_medicao`:**
   - Isola a camada de física/metrologia avançada, registrando o cálculo da incerteza expandida ($U$) e o fator de abrangência ($k$) para cada medição específica (`fk_medicao_id`).

## 3. Justificativa Técnica: Normalização e Eliminação de Anomalias
No modelo original baseado em Excel, informações de metrologistas, dados do equipamento, especificações de máquina MMC e tolerâncias eram repetidos linha a linha. Essa redundância gerava sérias anomalias operacionais:

* **Inconsistência de Dados (Redundância):** Variações de grafia em nomes de fornecedores, setores e técnicos entre diferentes planilhas.
* **Riscos em Auditorias ISO/IEC 17025:** Risco de alteração não autorizada nos limites de tolerância ou nas dimensões nominais de referência.
* **Dificuldade de Atualização:** A alteração de um dado cadastral (ex: mudança de turno de um metrologista ou de setor de um instrumento) exigia a alteração de múltiplos arquivos antigos.

A modelagem relacional aplicada alcança a **Terceira Forma Normal (3FN)**:
- **Chaves Primárias Únicas (`PK`):** Todos os cadastros base (técnicos, instrumentos, máquinas e setores) possuem identificadores exclusivos.
- **Integridade Referencial com Chaves Estrangeiras (`FK`):** A amarração do banco obriga que todo certificado e toda medição pertençam a entidades válidas. As restrições `ON DELETE RESTRICT` impedem a exclusão acidental de cadastros que possuam histórico de calibração associado.

## 5. Diagrama Relacional de Blocos
![Diagrama de Entidade Relacionamento](./DER%20Lógico%20-%20Banco%20Schulz.png)
