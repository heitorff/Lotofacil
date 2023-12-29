from collections import Counter
from datetime import datetime
from dateutil import relativedelta
from PySimpleGUI import PySimpleGUI as sg
import functions




if __name__ == '__main__':

    sg.theme('Reddit')

    numeros_par = ['11', '12', '13', '14', '15']

    arquivo_resultados = 'resultados_lotofacil.json'

    resultados_lotofacil = functions.ler_resultados_arquivo(arquivo_resultados)

    if not resultados_lotofacil:
        resultados_lotofacil = functions.obter_resultados_lotofacil()
        functions.gravar_resultados_arquivo(resultados_lotofacil, arquivo_resultados)

    #resultados_lotofacil = obter_resultados_lotofacil()

    if resultados_lotofacil:

        numero_qtd = []
        semestre = []
        par  = []


        layout = [
            [sg.Text("Últimos resultados da Lotofácil: (Obrigatório o preenchimento da data)")],
            [sg.Text('Digite a data de início do intervalo (formato MM/YYYY): '), sg.Input(key="data_inicio")],
            [sg.Text('Digite a data de fim do intervalo (formato MM/YYYY): '), sg.Input(key="data_fim")],
            [sg.Button('Escolher numeros'), sg.Button('Sair'), sg.Button('Atualizar'), sg.Text('Status Atualização!', key='status')],
            [sg.Text('Números da sua aposta:')],
            [sg.Text(key='numero_aposta')],
            [sg.Text('Número de vezes que cada número foi sorteado:')],
            [sg.Listbox(key='numero_individual', values = numero_qtd, s=(60, 5))],
            [sg.Text('Número de vezes que o conjunto completo foi sorteado:')],
            [sg.Text(key='conjunto_final')],
            [sg.Text('Total de sorteios por semestre:')],
            [sg.Listbox(key='semestre', values = semestre, s=(60, 5))],
            [sg.Text('Número de vezes que cada par de 11 a 15 foi sorteado:')],
            [sg.Listbox(key='pares', values = par, s=(60, 5))],
            [sg.Button('Resultados')]
        ]

        window = sg.Window('Lotofácil Analyzer', layout)    

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == 'Sair':
                break
            elif event == 'Escolher numeros':
                #sg.popup('Selecione os números da sua aposta.')
                numeros_aposta_usuario = functions.numero_aposta()
            elif event == 'Resultados':

                numero_qtd = []
                semestre = []
                pares = []
                window['numero_aposta'].update(value=numeros_aposta_usuario)

                data_inicio = datetime.strptime((values['data_inicio']), "%m/%Y")
                data_fim = datetime.strptime((values['data_fim']), "%m/%Y")

                intervalo_meses = functions.criar_intervalo_meses(data_inicio, data_fim)

                resultados_filtrados = functions.excluir_resultados_indesejados(resultados_lotofacil, numeros_aposta_usuario)

                contagem_individual, contagem_conjunto, contagem_conjunto_total, contagem_conjunto_semestre, contagem_semestre  = functions.contar_acertos(resultados_lotofacil, numeros_aposta_usuario)

                
                for numero, contagem in contagem_individual.items():
                    numero_qtd.append(f"Número {numero}: {contagem} vezes.")
                window['numero_individual'].update(values=numero_qtd)

                conjunto_formatado = tuple(numeros_aposta_usuario)
                conjunto_final = f"Conjunto {conjunto_formatado}: {contagem_conjunto_total[conjunto_formatado]} vezes."
                window['conjunto_final'].update(value=conjunto_final)

                
                for semestre_ano, total in contagem_semestre.items():
                    semestre.append(f"Semestre/Ano: {semestre_ano}, Total de sorteios: {total}")
                window['semestre'].update(values=semestre)

                contagem_pares = functions.contar_pares_sorteio(resultados_lotofacil, numeros_par, intervalo_meses)

                
                for par, total in contagem_pares.items():
                    pares.append(f"Par {par[0]}-{par[1]}: {total} vezes (Semestre/Ano: {par[2]})")
                window['pares'].update(values=pares)  

            elif event == 'Atualizar':
                window['status'].update("Iniciando Atualização!")
                resultados_lotofacil = functions.obter_resultados_lotofacil()
                functions.gravar_resultados_arquivo(resultados_lotofacil, arquivo_resultados)