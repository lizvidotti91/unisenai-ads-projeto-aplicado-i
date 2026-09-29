| Tabela                 | Campo                | Tipo de Dado | Obrigatório | Observação                                          |
| ---------------------- | -------------------- | ------------ | ----------- | --------------------------------------------------- |
| FORNECEDOR_SETOR       | id                   | Texto        | sim         | Chave primária (PK)                                 |
| FORNECEDOR_SETOR       | sigla_fornecedor     | Texto        | sim         | Identificação do fornecedor                         |
| FORNECEDOR_SETOR       | setor                | Texto        | sim         | Setor do fornecedor                                 |
| FORNECEDOR_SETOR       | responsavel_cadastro | Texto        | sim         | Responsável pelo cadastro                           |
| INSTRUMENTO            | id                   | Texto        | sim         | Chave primária (PK)                                 |
| INSTRUMENTO            | tag_equipamento      | Texto        | sim         | Identificação do equipamento; UNIQUE                |
| INSTRUMENTO            | numero_serie         | Texto        | sim         | Número de série do instrumento; UNIQUE              |
| INSTRUMENTO            | fabricante           | Texto        | não         | Fabricante do instrumento                           |
| INSTRUMENTO            | drawing_no           | Texto        | não         | Número do desenho do instrumento                    |
| INSTRUMENTO            | part_no              | Texto        | não         | Número da peça                                      |
| INSTRUMENTO            | fk_fornecedor_id     | Texto        | sim         | Chave estrangeira (FK)                              |
| METROLOGISTA           | id                   | Texto        | sim         | Chave primária (PK)                                 |
| METROLOGISTA           | matricula            | Texto        | sim         | Identificação do metrologista                       |
| METROLOGISTA           | nome_metrologista    | Texto        | não         | Nome do metrologista                                |
| METROLOGISTA           | turno                | Texto        | não         | Turno de trabalho                                   |
| MAQUINA_MMC            | id                   | Texto        | sim         | Chave primária (PK)                                 |
| MAQUINA_MMC            | codigo_mmc           | Texto        | sim         | Código de identificação MMC                         |
| MAQUINA_MMC            | measurement_plan     | Texto        | não         | Plano de medição utilizado                          |
| MAQUINA_MMC            | hora_medicao         | Texto        | não         | Horário em que a medição foi realizada              |
| CERTIFICADO_CALIBRACAO | id                   | Texto        | sim         | Chave primária (PK)                                 |
| CERTIFICADO_CALIBRACAO | numero_certificado   | Texto        | sim         | Número de identificação do certificado; UNIQUE      |
| CERTIFICADO_CALIBRACAO | data_calibracao      | Texto        | sim         | Data de realização da calibração                    |
| CERTIFICADO_CALIBRACAO | status_conformidade  | Texto        | sim         | Resultado da conformidade                           |
| CERTIFICADO_CALIBRACAO | fk_metrologista_id   | Texto        | sim         | Chave estrangeira (FK)                              |
| CERTIFICADO_CALIBRACAO | fk_instrumento_id    | Texto        | sim         | Chave estrangeira (FK)                              |
| CERTIFICADO_CALIBRACAO | fk_mmc_id            | Texto        | sim         | Chave estrangeira (FK)                              |
| MEDICAO_CARACTERISTICA | id                   | Texto        | sim         | Chave primária (PK)                                 |
| MEDICAO_CARACTERISTICA | nome_caracteristica  | Texto        | sim         | Parâmetro/característica medida                     |
| MEDICAO_CARACTERISTICA | eixo_referencia      | Texto        | não         | Eixo utilizado como referência na medição           |
| MEDICAO_CARACTERISTICA | valor_nominal        | Real         | sim         | Valor de referência                                 |
| MEDICAO_CARACTERISTICA | tolerancia_superior  | Real         | sim         | Limite superior                                     |
| MEDICAO_CARACTERISTICA | tolerancia_inferior  | Real         | sim         | Limite inferior                                     |
| MEDICAO_CARACTERISTICA | valor_atual          | Real         | sim         | Valor obtido na medição                             |
| MEDICAO_CARACTERISTICA | desvio               | Real         | sim         | Diferença em relação ao valor nominal e valor atual |
| MEDICAO_CARACTERISTICA | fk_certificado_id    | Texto        | sim         | Chave estrangeira (FK)                              |
| INCERTEZA_MEDICAO      | id                   | Texto        | sim         | Chave primária (PK)                                 |
| INCERTEZA_MEDICAO      | incerteza_expandida  | Real         | sim         | Valor da incerteza expandida da medição             |
| INCERTEZA_MEDICAO      | fator_k              | Real         | não         | Fator de abrangência utilizado no cálculo           |
| INCERTEZA_MEDICAO      | fk_medicao_id        | Texto        | sim         | Chave estrangeira (FK)                              |
