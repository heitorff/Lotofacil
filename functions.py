import requests
import time
from collections import Counter
from datetime import datetime
import json
import os
from dateutil import relativedelta
from PySimpleGUI import PySimpleGUI as sg


#Faço essa requisição da API para pegar o ultimo concurso para usar no While
resultados = []
url = 'https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/'
response = requests.get(url)
response.raise_for_status()
dados = response.json()
concurso = dados.get('numero')
x = True
i = 1

def obter_resultados_lotofacil():
    x = True
    i = 1
    resultados = {}
    
    
    while x == True:
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{i}"
        

        try:
            #for numero in range(1,concurso):
                #anteriores = f'{numero:04}'
            response = requests.get(url)
            response.raise_for_status()
            dados = response.json()
            if 'error' in dados:
                print(f"Erro na API: {dados['error']}")
                return None
            
            
            dezena = f'dezenas{i}' 
            data =  f'data{i}'         
            resultados_parcial = {dezena: dados['listaDezenas'], data: dados['dataApuracao']}
            resultados.update(resultados_parcial)
            

            i+=1
            if i > concurso:
                    resultados_final = {'resultados': []}

                    num_pares = len([chave for chave in resultados.keys() if chave.startswith('dezena')])

                    for i in range(1, num_pares + 1):
                        chave_dezena = f'dezenas{i}'
                        chave_data = f'data{i}'

                        valor_dezena = resultados.get(chave_dezena)
                        valor_data = resultados.get(chave_data)

                        if valor_dezena is not None and valor_data is not None:
                            resultados_final['resultados'].append({'dezenas': valor_dezena, 'data': valor_data})
                   
                    window["status"].update("Atualização Encerrada!")
                    return resultados_final
                    x = False    
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            time.sleep(3)
        continue

def gravar_resultados_arquivo(resultados, arquivo):
    with open(arquivo, 'w') as file:
        json.dump(resultados, file)

def ler_resultados_arquivo(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as file:
            return json.load(file)
    else:
        return None


def numero_aposta():
    numeros_aposta = []

    layout = [
        [sg.Text('Digite um número entre 1 e 25 para sua aposta (digite 0 para parar):')],
        [sg.InputText(key='numero')],
        [sg.Button('Adicionar'), sg.Button('Parar')],
    ]

    window = sg.Window('Comprar Aposta', layout)

    while True:
        event, values = window.read()

        
        if event == sg.WINDOW_CLOSED or event == 'Parar' or len(numeros_aposta) > 15:
            break
        elif event == 'Adicionar':
                    try:
                        if values['numero'] not in numeros_aposta:
                            numeros_aposta.append(values['numero'])
                            sg.popup('Adicionado!')
                        else:
                            print("Número inválido ou já escolhido. Tente novamente.")
                    except ValueError:
                        print("Entrada inválida. Digite um número inteiro.")
    
    window.close()
    return numeros_aposta

def excluir_resultados_indesejados(resultados, numeros_aposta):
    resultados_filtrados = []

    for resultado in resultados['resultados']:
        if all(num in resultado['dezenas'] for num in numeros_aposta):
            resultados_filtrados.append(resultado)

    return resultados_filtrados


def contar_acertos(resultados, numeros_aposta):
    contagem_individual = Counter()
    contagem_conjunto = Counter()
    contagem_conjunto_total = Counter()
    contagem_conjunto_semestre = Counter()
    contagem_semestre = Counter()
    contagem_conjunto_final = Counter()

    numeros_aposta_str = list(map(str, numeros_aposta))

    for resultado in resultados['resultados']:
        for numero in numeros_aposta:
            if numero in resultado['dezenas']:
                contagem_individual[numero] += 1

        #conjunto_igual = set(numeros_aposta) == set(resultado)
        #if conjunto_igual:
           # contagem_conjunto[tuple(numeros_aposta)] += 1

    #for resultado in resultados:
        conjunto_igual = set(numeros_aposta) <= set(resultado['dezenas'])
        if conjunto_igual:
            data_sorteio = datetime.strptime(resultado['data'], "%d/%m/%Y")
            semestre_ano = f"{data_sorteio.day:02d}/{data_sorteio.month:02d}/{data_sorteio.year}"
            contagem_conjunto[(tuple(numeros_aposta), resultado['data'])] += 1
            contagem_conjunto_semestre[(tuple(numeros_aposta), semestre_ano)] += 1
            contagem_conjunto_total[tuple(numeros_aposta)] += 1
            
            semestre = (data_sorteio.month - 1) // 6 + 1
            semestre_ano_separado = f"{semestre}/{data_sorteio.year}"

            contagem_semestre[semestre_ano_separado] += 1
            
        

    return contagem_individual, contagem_conjunto, contagem_conjunto_total, contagem_conjunto_semestre, contagem_semestre

def contar_pares_sorteio(resultados, numeros_aposta, intervalo_meses):
    contagem_pares = Counter()

    for num1 in numeros_aposta:
        for num2 in numeros_aposta:
            if num1 < num2:
                for resultado in resultados['resultados']:
                    if num1 in resultado['dezenas'] and num2 in resultado['dezenas'] and all(num not in resultado['dezenas'] for num in numeros_aposta if num != num1 and num != num2):
                        data_sorteio = datetime.strptime(resultado['data'], "%d/%m/%Y")
                        mes_ano = f"{data_sorteio.month:02d}/{data_sorteio.year}"

                        if mes_ano in intervalo_meses:
                            contagem_pares[(num1, num2, mes_ano)] += 1

    return contagem_pares


def criar_intervalo_meses(data_inicio, data_fim):
    intervalo_meses = set()

    data_atual = data_inicio
    while data_atual <= data_fim:
        intervalo_meses.add(data_atual.strftime("%m/%Y"))
        data_atual += relativedelta.relativedelta(months=1)

    return intervalo_meses
