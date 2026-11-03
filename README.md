# Projeto Aplicado I — Automação do Processo Metrológico (Schulz S.A.)
* **Curso:** Análise e Desenvolvimento de Sistemas (ADS)
* **Instituição:** UniSENAI
* **Disciplina:** Projeto Aplicado I
* **Professor(a):** Hugo Menezes Barra

### Integrantes
* [Caio Montinegro Barbosa](https://github.com/caiomsenai)
* [Elisete Cristina Vidotti da Rocha](https://github.com/lizvidotti91)
* Gabriela da Silva Brand
* Julio Cesar Braga

## Escopo das Entregas

* [**Desafio 02 — Modelagem e estruturação do banco de dados**](./Desafio%202/)
    * `01_estrutura.md`: Apresenta a divisão do banco entre as três entidades
    * `02_dicionario.md`: Dicionário de dados mapeando tipos, restrições e regras de negócio de cada campo.
    * `03_banco.sql`: Script DDL executável para criação do banco de dados `schulz.db`.

- [**Desafio 03 — Construção MVP Parte 1**](./Desafio%203/)
    - `classes/`: Apresenta as classes principais (`TecnicoSolicitante`, `Equipamento`, `Medicao`) com as respectivas regras de negócio de cada uma
    - `database/`: Apresenta as classes de conexão com o banco baseadas no padrão DAO (`TecnicoDAO`, `EquipamentoDAO`, `MedicaoDAO`), onde cada classe tem responsabilidade única
  - **`04_classes.py`**: Ponto único de importação centralizada para todas as classes (principais e de conexão com o banco de dados).
  - **`05_main.py`**: Script de demonstração que executa o fluxo funcional completo (criação do banco, injeção de dados de teste, validação metrológica de status, atualização de registos reprovados, tratamento de erros de SQL e impressão do Relatório de Calibração).

## Tecnologias Utilizadas
* **SGBD:** SQLite
* **Linguagem SQL:** DDL (Data Definition Language)
* **Programação Orientada a Objetos** Python