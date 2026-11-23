import os
from datetime import datetime, date, time
import openpyxl

from database import ConexaoBanco
from .tecnico_service import TecnicoService
from .equipamento_service import EquipamentoService
from .medicao_service import MedicaoService


class IngestaoService:
    # Inicializacao
    def __init__(self, conexao: ConexaoBanco):
        self.conexao = conexao # conexao do banco de dados
        self.tecnico_srv = TecnicoService(conexao) # instancia o objeto TecnicoService
        self.equipamento_srv = EquipamentoService(conexao) # instancia o objeto EquipamentoService
        self.medicao_srv = MedicaoService(conexao) #Instancia o objeto MedicaoService

    # Metodo responsavel por converter data e hora do Excel para o padrão do banco (AAAA-MM-DD HH:MM:SS)
    def formatar_data_hora(self, valor_data, valor_hora=None):
        data_limpa = self.medicao_srv.limpar_nulo(valor_data)
        if data_limpa is None:
            return None

        data_convertida = None
        if isinstance(data_limpa, datetime): # Verifica se data_limpa é do tipo datetime
            data_convertida = data_limpa.date() # converte para o tipo date
        elif isinstance(data_limpa, date): # verifica se data_limpa é do tipo date
            data_convertida = data_limpa # armazena o valor
        else:
            texto_data = str(data_limpa).strip() # se o tipo for string, remove espacos adicionais
            for formato in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"): # verifica se a string está em algum dos formatos de data brasileiros
                try:
                    data_convertida = datetime.strptime(texto_data, formato).date() # converte para date
                    break
                except ValueError:
                    continue # tratamento de erros

        if data_convertida is None:
            return None

        # hora padrão
        hora_texto = "00:00:00"
        hora_limpa = self.medicao_srv.limpar_nulo(valor_hora)

        if isinstance(hora_limpa, (datetime, time)): # verifica se hora_limpa é do tipo datetime
            hora_texto = hora_limpa.strftime("%H:%M:%S") # converte para string no formato hora:minuto:segundo
        elif isinstance(hora_limpa, str): # verifica se hora_limpa é do tipo string
            sem_milissegundos = hora_limpa.split(".")[0].strip()
            partes = sem_milissegundos.split(":") # converte para array, separando hora, minuto, segundo pelos delimitadores :
            if len(partes) >= 2:
                hora = partes[0].zfill(2)
                minuto = partes[1].zfill(2)

                segundo = "00"
                if len(partes) > 2: # se os segundos forem maiores do que zero
                    segundo = partes[2].zfill(2)
                
                hora_texto = f"{hora}:{minuto}:{segundo}" # formata a string para o padrao hora:minuto: segundo

        return f"{data_convertida.strftime('%Y-%m-%d')} {hora_texto}" # retorna a string formatada para o padrao do banco de dados "YYYY-MM-DD HH:MM:SS"

    # Metodo responsavel por procurar o primeiro valor preenchido à direita de um rótulo na mesma linha
    def _buscar_valor_a_direita(self, linha, indice_atual):
        for coluna in range(indice_atual + 1, len(linha)):
            celula = linha[coluna]
            if celula is not None and str(celula).strip() != "":
                return celula
        return None

    # Metodo responsavel por ler os dados do cabeçalho da aba Registro
    def ler_aba_registro(self, planilha):
        # Objeto no padrao para enviar ao service
        dados = {
            "data": None,
            "solicitante": None,
            "metrologista": None,
            "padrao_codigo": "MMC-500.008",
            "tag": None,
            "denominacao": "Dispositivo de Controle",
            "fabricante": None,
        }

        if "Registro" not in planilha.sheetnames:
            return dados # se nao for encontrada a aba Registros, retorna o objetos dados vazio

        aba = planilha["Registro"]
        for linha in aba.iter_rows(values_only=True): # percorre cada linha da aba Registro
            for i in range(len(linha)): # percorre cada célula da linha
                celula = linha[i] # armazena o valor da celula
                if not isinstance(celula, str):
                    continue # se a célula for invalida, pula para a proxima celula da linha

                rotulo = celula.strip().lower().rstrip(":") # armazena o valor da coluna
                valor = self._buscar_valor_a_direita(linha, i) # armazena o valor da celula

                # Faz o de/para entre as linhas do excel e o objeto para ser enviado ao service
                if rotulo == "data" and dados["data"] is None:
                    dados["data"] = valor
                elif rotulo == "cliente solicitante":
                    dados["solicitante"] = valor
                elif rotulo in ("técnico executante", "tecnico executante"):
                    dados["metrologista"] = valor
                elif rotulo in ("código", "codigo") and dados["tag"] is None:
                    dados["tag"] = valor
                elif rotulo in ("denominação", "denominacao"):
                    dados["denominacao"] = valor
                elif rotulo == "fabricante":
                    dados["fabricante"] = valor

        return dados

    # Metodo responsavel por ler o cabeçalho e a tabela de medições da aba "Importação"
    def ler_aba_importacao(self, planilha):
        # Verifica se o excel contem a aba Importacao
        if "Importação" in planilha.sheetnames:
            aba = planilha["Importação"]
        elif "Importacao" in planilha.sheetnames:
            aba = planilha["Importacao"]
        else:
            raise ValueError("Aba 'Importação' não encontrada na planilha.") # Tratamento de erros

        cabecalho = {"programa": None, "date": None, "time": None} # Objeto no padrao a ser enviado para o service
        linha_cabecalho_tabela = None

        # Procura os dados do topo e onde começa a tabela (linha com "DIMENSION")
        for num_linha, linha in enumerate(aba.iter_rows(values_only=True), start=1):
            if not linha:
                continue # se a linha for invalida, pula para a proxima linha
            primeira_celula = ""
            if linha[0] is not None:
                primeira_celula = str(linha[0]).strip().lower() #armazena o valor da primeira celula

            # Faz o de/para entre os valores da tabela e o objeto cabecalho
            if primeira_celula.startswith("part program name"):
                cabecalho["programa"] = self._buscar_valor_a_direita(linha, 0)
            elif primeira_celula.startswith("date"):
                cabecalho["date"] = self._buscar_valor_a_direita(linha, 0)
            elif primeira_celula.startswith("time"):
                cabecalho["time"] = self._buscar_valor_a_direita(linha, 0)
            else:
                # Verifica se esta linha é o cabeçalho da tabela de medições
                for celula in linha:
                    if celula is not None and str(celula).strip().lower() == "dimension":
                        linha_cabecalho_tabela = num_linha
                        break

            if linha_cabecalho_tabela is not None:
                break

        if linha_cabecalho_tabela is None:
            raise ValueError("Cabeçalho 'DIMENSION' não encontrado na aba Importação.") # tratamento de erros

        # Descobre em qual coluna está cada título (DIMENSION, NOMINAL, +TOL, etc.)
        posicoes = {}
        for idx_col, celula in enumerate(aba[linha_cabecalho_tabela]):
            if celula.value is not None:
                nome_coluna = str(celula.value).strip().upper()
                posicoes[nome_coluna] = idx_col

        colunas_obrigatorias = ["DIMENSION", "NOMINAL", "+TOL", "-TOL", "MEAS 1", "MEAS 2"]
        # Validar se a coluna possui todos os valores obrigatorios para a medicao
        for col in colunas_obrigatorias:
            if col not in posicoes:
                raise ValueError(f"Coluna obrigatória '{col}' não encontrada na aba Importação.")

        # Lê todas as linhas abaixo do cabeçalho
        linhas_medicoes = []
        for num_linha in range(linha_cabecalho_tabela + 1, aba.max_row + 1):
            linha = [celula.value for celula in aba[num_linha]]
            dimensao = linha[posicoes["DIMENSION"]]
            
            # Faz o de/para entre as informacoes da tabela e o objeto para ser enviado ao service
            if self.medicao_srv.limpar_nulo(dimensao) is not None:
                linhas_medicoes.append({
                    "dimension": dimensao,
                    "nominal": linha[posicoes["NOMINAL"]],
                    "tol_sup": linha[posicoes["+TOL"]],
                    "tol_inf": linha[posicoes["-TOL"]],
                    "meas_1": linha[posicoes["MEAS 1"]],
                    "meas_2": linha[posicoes["MEAS 2"]],
                })

        return cabecalho, linhas_medicoes

    # Metodo principal para ler a planilha e guardar as informacoes no banco
    def importar_planilha(self, caminho_arquivo, tag_manual=None, metrologista_manual=None):
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}") # tratamento de erros

        planilha = openpyxl.load_workbook(caminho_arquivo, data_only=True)
        dados_registro = self.ler_aba_registro(planilha)
        cabecalho_imp, linhas_brutas = self.ler_aba_importacao(planilha)

        # Prioriza o que foi digitado manualmente na tela; se não houver, usa o da planilha
        tag = self.medicao_srv.limpar_nulo(tag_manual or dados_registro["tag"])
        metrologista = metrologista_manual or dados_registro["metrologista"]
        data_bruta = dados_registro["data"] or cabecalho_imp["date"]
        data_hora_iso = self.formatar_data_hora(data_bruta, cabecalho_imp["time"])

        if not tag or not metrologista or not data_hora_iso:
            raise ValueError("Bloqueio ETL: Tag do equipamento, Metrologista ou Data válida ausentes.") # tratamento de erros

        # Salva ou busca os cadastros principais usando os outros Services
        id_metrologista = self.tecnico_srv.salvar(metrologista, "METROLOGISTA", "Metrologia")

        id_solicitante = None
        if self.medicao_srv.limpar_nulo(dados_registro["solicitante"]) is not None:
            setor_solicitante = str(dados_registro["solicitante"])
            id_solicitante = self.tecnico_srv.salvar(setor_solicitante, "SOLICITANTE", setor_solicitante)

        id_padrao = self.equipamento_srv.salvar(
            dados_registro["padrao_codigo"], "MMC", "502390",
            "Maquina de Medicao por Coordenadas", "Carl Zeiss"
        )
        id_instrumento = self.equipamento_srv.salvar(
            str(tag), "INSTRUMENTO", f"SN-{tag}",
            dados_registro["denominacao"], dados_registro["fabricante"], id_solicitante
        )

        # Remove características repetidas (mantém a última leitura da planilha)
        medicoes_unicas = {}
        for item in linhas_brutas:
            codigo_limpo = self.medicao_srv.limpar_codigo_caracteristica(item["dimension"])
            if codigo_limpo is not None:
                medicoes_unicas[codigo_limpo] = item

        # Salva cada medição higienizada no banco
        salvos = 0
        alertas = []
        erros = []
        contador = 1

        for item in medicoes_unicas.values():
            codigo_item = f"C{contador:02d}"
            medicao, mensagem = self.medicao_srv.salvar(
                equipamento_id=id_instrumento,
                padrao_id=id_padrao,
                tecnico_id=id_metrologista,
                dt_hora_iso=data_hora_iso,
                plano_medicao=cabecalho_imp["programa"],
                codigo=codigo_item,
                parametro_bruto=item["dimension"],
                nominal_bruto=item["nominal"],
                tol_sup_bruto=item["tol_sup"],
                tol_inf_bruto=item["tol_inf"],
                meas1_bruto=item["meas_1"],
                meas2_bruto=item["meas_2"],
            )

            if medicao is not None:
                salvos += 1
                if mensagem is not None:
                    alertas.append(mensagem)
            elif mensagem is not None:
                erros.append(mensagem)

            contador += 1

        return {
            "sucesso": True,
            "equipamento_tag": str(tag),
            "registros_salvos": salvos,
            "alertas": alertas,
            "erros": erros,
        }