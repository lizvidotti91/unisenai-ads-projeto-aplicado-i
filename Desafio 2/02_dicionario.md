# Dicionário de Dados do Sistema — Projeto Aplicado I (Schulz S.A.)

Banco: SQLite · Script de criação: `03_banco.sql` · **3 tabelas, 39 campos mapeados**.
Tipos usados: **Texto** (`TEXT`), **Real** (`REAL`) e **Inteiro** (`INTEGER`).
Datas são guardadas como Texto no formato ISO 8601 (`AAAA-MM-DD HH:MM:SS`).

## Tabela `tecnico_solicitante`

| Campo | Tipo | Obrigatório | Chave / Restrição | Descrição |
|---|---|---|---|---|
| `id_tecnico` | Inteiro | Sim | PK | Identificador único do técnico ou solicitante |
| `matricula` | Texto | Não | UNIQUE | Matrícula do funcionário (solicitante externo pode não ter) |
| `nome` | Texto | Sim | — | Nome completo |
| `cargo` | Texto | Não | — | Cargo ou função na empresa |
| `papel` | Texto | Sim | CHECK: METROLOGISTA, SIGNATARIO, SOLICITANTE | Papel da pessoa no processo de calibração |
| `setor` | Texto | Não | — | Setor de atuação ou de origem do solicitante |
| `turno` | Texto | Não | CHECK: MATUTINO, VESPERTINO, NOTURNO | Turno de trabalho |
| `ativo` | Inteiro | Sim | CHECK: 0 ou 1; padrão 1 | Cadastro ativo (1) ou inativo (0), sem apagar o histórico |

## Tabela `equipamento`

| Campo | Tipo | Obrigatório | Chave / Restrição | Descrição |
|---|---|---|---|---|
| `id_equipamento` | Inteiro | Sim | PK | Identificador único do equipamento |
| `tag_equipamento` | Texto | Sim | UNIQUE | TAG ou código de identificação (ex.: código do padrão) |
| `tipo` | Texto | Sim | CHECK: MMC, INSTRUMENTO | MMC (padrão) ou instrumento/dispositivo calibrado |
| `numero_serie` | Texto | Sim | UNIQUE | Número de série do fabricante |
| `nome_equipamento` | Texto | Sim | — | Nome do equipamento |
| `fabricante` | Texto | Sim | Padrão 'NAO INFORMADO' | Fabricante |
| `modelo` | Texto | Não | — | Modelo |
| `faixa_medicao` | Texto | Não | — | Faixa ou volume de medição (ex.: 700x1000x600 mm) |
| `drawing_no` | Texto | Não | — | Número do desenho técnico |
| `part_no` | Texto | Não | — | Número da peça |
| `rastreabilidade` | Texto | Não | — | Certificado que dá rastreabilidade ao padrão |
| `fk_solicitante_id` | Inteiro | Não | FK → `tecnico_solicitante.id_tecnico` | Dono ou solicitante (nulo para equipamento interno) |

## Tabela `medicao`

| Campo | Tipo | Obrigatório | Chave / Restrição | Descrição |
|---|---|---|---|---|
| `id_medicao` | Inteiro | Sim | PK | Identificador único da medição |
| `fk_equipamento_id` | Inteiro | Sim | FK → `equipamento.id_equipamento` | Equipamento calibrado |
| `fk_padrao_id` | Inteiro | Não | FK → `equipamento.id_equipamento` | MMC ou padrão utilizado na medição |
| `fk_tecnico_id` | Inteiro | Sim | FK → `tecnico_solicitante.id_tecnico` | Metrologista que executou a medição |
| `numero_certificado` | Texto | Não | — | Número do certificado (preenchido na emissão) |
| `data_hora_medicao` | Texto | Sim | — | Data e hora da medição (ISO 8601) |
| `plano_medicao` | Texto | Não | — | Programa (measurement plan) executado no Calypso |
| `codigo` | Texto | Sim | UNIQUE com equipamento e data/hora | Código da característica medida |
| `parametro` | Texto | Sim | — | Parâmetro medido (ex.: diâmetro, planicidade) |
| `eixo_referencia` | Texto | Não | — | Eixo de referência da medição |
| `unidade` | Texto | Sim | CHECK: mm, um, graus; padrão mm | Unidade de medida dos valores |
| `valor_nominal` | Real | Sim | — | Valor nominal de referência |
| `tolerancia_superior` | Real | Não | CHECK: ≥ inferior | Tolerância superior (nulo se unilateral) |
| `tolerancia_inferior` | Real | Não | — | Tolerância inferior (nulo se unilateral) |
| `medida_1` | Real | Sim | — | Primeira medição da característica |
| `medida_2` | Real | Não | — | Segunda medição da característica |
| `valor_obtido` | Real | Sim | — | Valor final obtido (Actual) |
| `desvio` | Real | Sim | CHECK: = valor_obtido − valor_nominal | Desvio em relação ao nominal |
| `status` | Texto | Sim | CHECK: APROVADO, REPROVADO, PENDENTE; padrão PENDENTE | Resultado da característica |

## Resumo

| Tabela | Campos | Inteiro | Real | Texto |
|---|---|---|---|---|
| `tecnico_solicitante` | 8 | 2 | 0 | 6 |
| `equipamento` | 12 | 2 | 0 | 10 |
| `medicao` | 19 | 4 | 7 | 8 |
| **Total** | **39** | **8** | **7** | **24** |

## Padronização dos nomes de colunas (planilha da MMC → banco)

Os dados vêm da planilha gerada pelo software da MMC (Calypso) na calibração do dispositivo, analisada na Entrega 01. Os nomes originais foram padronizados em `snake_case`, sem acento e sem espaços.

| Coluna original da planilha | Campo padronizado | Tabela | Observação |
|---|---|---|---|
| Characteristic | `codigo` e `parametro` | `medicao` | `codigo` guarda o nome original; `parametro` é o nome sem o prefixo numérico (ex.: `62P_`) |
| Nominal | `valor_nominal` | `medicao` | — |
| Upper Tol (antes grafado "Upper Tool") | `tolerancia_superior` | `medicao` | Vazio = tolerância unilateral |
| Lower Tol | `tolerancia_inferior` | `medicao` | Vazio = tolerância unilateral |
| Actual (1º bloco) | `medida_1` | `medicao` | Primeira medição |
| Actual (2º bloco) | `medida_2` | `medicao` | Segunda medição |
| (calculado) | `valor_obtido` | `medicao` | Média de `medida_1` e `medida_2`; quando só existe `medida_1`, é igual a ela |
| Deviation | `desvio` | `medicao` | Passa a ser sempre `valor_obtido − valor_nominal` |
| (calculado) | `status` | `medicao` | APROVADO ou REPROVADO, conforme as tolerâncias |
| Measurement plan | `plano_medicao` | `medicao` | Programa executado |
| Data/hora da medição | `data_hora_medicao` | `medicao` | ISO 8601 |
| Drawing no. / Part no. | `drawing_no` / `part_no` | `equipamento` | — |
| Matrícula do metrologista | `matricula` | `tecnico_solicitante` | — |

## Correspondência com os campos de referência do roteiro

| Entidade | Campo de referência | Campo no banco |
|---|---|---|
| Técnico/Solicitante | ID do técnico | `id_tecnico` |
| Técnico/Solicitante | Nome | `nome` |
| Técnico/Solicitante | Matrícula | `matricula` |
| Técnico/Solicitante | Cargo | `cargo` |
| Equipamento | Código/Tag do equipamento | `tag_equipamento` |
| Equipamento | Nome do equipamento | `nome_equipamento` |
| Equipamento | Parâmetro | `parametro` (tabela `medicao`, ver nota) |
| Equipamento | Valor nominal | `valor_nominal` (tabela `medicao`, ver nota) |
| Medição | ID da medição | `id_medicao` |
| Medição | Tolerância superior/inferior | `tolerancia_superior` / `tolerancia_inferior` |
| Medição | Valor obtido | `valor_obtido` |
| Medição | Data da medição | `data_hora_medicao` |

**Nota:** `parametro` e `valor_nominal` ficam na tabela `medicao` porque cada equipamento tem vários parâmetros, cada um com seu nominal. Se fossem colunas de `equipamento`, a tabela teria uma linha por parâmetro e repetiria TAG e número de série, o que contraria o objetivo de evitar duplicidade. A tabela `parametro_equipamento` está prevista como evolução (ver `01_estrutura.md`).