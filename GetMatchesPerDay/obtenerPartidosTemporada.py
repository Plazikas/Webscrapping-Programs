'''
# Programa que toma todos los resultados y la dirección para acceder al acta de cada partido
'''

from decimal import localcontext
from threading import local
from turtle import title
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

# Función para convertir las tres miras letras de un mes en su número correspondiente
def convertirMesANumero(mes):
    if (mes == 'Ene'):
        return 1
    elif (mes == 'Feb'):
        return 2 
    elif (mes == 'Mar'):
        return 3
    elif (mes == 'Abr'):
        return 4
    elif (mes == 'May'):
        return 5
    elif (mes == 'Jun'):
        return 6
    elif (mes == 'Jul'):
        return 7
    elif (mes == 'Ago'):
        return 8
    elif (mes == 'Sep'):
        return 9
    elif (mes == 'Oct'):
        return 10
    elif (mes == 'Nov'):
        return 11
    elif (mes == 'Dic'):
        return 12

# Función para comprobar si un partido se ha jugado ya o no
def PartidoJugado(fechaPartido):
    now = datetime.now()

    if ( int((str(now.year)[2:])) > int(fechaPartido[2]) ):
        return True
    elif (int((str(now.year)[2:])) < int(fechaPartido[2])):
        return False
    else:
        if (now.month > convertirMesANumero(fechaPartido[1])):
            return True
        elif (now.month < convertirMesANumero(fechaPartido[1])):
            return False
        else:
            if (now.day > int(fechaPartido[0])):
                return True
            elif (now.day < int(fechaPartido[0])):
                return False

temporada = 'temporada_22-23/'
dir_path = '/home/pedro/Escritorio/DatosFutbol/' + temporada

print(dir_path)

# Cargar el excel
excel_name = dir_path + 'partidos.xlsx'
excel_copia = 'Escritorio/DatosFutbol/partidoscopia.xlsx'

data_null = {}
df_null = pd.DataFrame(data_null)
df_null.to_excel(excel_name, index=False)
writer = pd.ExcelWriter(excel_name)

# Cargar la página web de resultados de fútbol
agent = {"User-Agent":"Mozilla/5.0"}

# Repetimos el proceso para la jornada
for i in range (1,39):
    # Obtenemos el código HTML de la página
    website = "https://www.resultados-futbol.com/primera/grupo1/jornada" + str(i) 
    result = requests.get(website, headers=agent)
    content = result.text

    soup = BeautifulSoup(content, 'lxml')
    box = soup.find('table', {"id":"tabla1"})
    table = box.find_all('tr', {'class':'vevent'})

    # Definimos las columnas del vector
    jornada = pd.DataFrame()
    locales = []
    visitantes = []
    goles_locales = []
    goles_visitantes = []
    direcciones_partidos = []

    # Obtenemos los datos de cada partido
    for match in table:

        # Obtenemos la fecha del partido
        horario_partido = match.find('td', {'class':'fecha'}).get_text()
        horario_partido = horario_partido.split()
        del horario_partido[-1]
    
        # Obtenemos los equipos que juegan el partido
        local_class = match.find('td', {'class':'equipo1'})
        local_name = local_class.find('a').get('href')[1:]

        visitante_class = match.find('td', {'class':'equipo2'})
        visitante_name = visitante_class.find('a').get('href')[1:]

        locales.append(local_name)
        visitantes.append(visitante_name)
            
        # Si el partido ya se ha jugado se obtiene el resultado y la dirección de la ficha del partido
        if (PartidoJugado (horario_partido) == True):

            match_name = match.find('span', {'class':'pt_match_name'}).find('a').get('href')

            resultado_total = match.find('a', {'class':'url'}).get_text()
            resultado = resultado_total.split('-')
            goles_local = resultado_total[0]
            goles_visitante = resultado_total[-1]

            direcciones_partidos.append(match_name)
            goles_locales.append(goles_local)
            goles_visitantes.append(goles_visitante)
        # Si el partido no se ha jugado se marca con un guión el resultado y la ficha del partido
        else:
            direcciones_partidos.append('-')
            goles_locales.append('-')
            goles_visitantes.append('-')
    
    # Añadimos las columnas al DataFrame
    jornada['Local'] = locales
    jornada['Goles Local'] = goles_locales
    jornada['Goles Visitante'] = goles_visitantes
    jornada['Visitante'] = visitantes
    jornada['Direcciones Partidos'] = direcciones_partidos

    # Añadimos la jornada como una hoja de excel   
    jornada.to_excel(writer, sheet_name='Jornada' + str(i), index=False)

    # Enviamos un mensaje de que la jornada ha sido añadida al excel
    print('Jornada ' + str(i) + ' añadida')

# Guardamos el excel y lo cerramos
writer.save()
writer.close()