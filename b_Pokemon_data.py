import requests
import pandas as pd
import time
import datetime
import math


def horas_dec_para_relog(horas_dec:float) -> str:#transformando as horas decimais em horas 00:00:00 para os graf interativos

  #tempo é uma lista com seus tempos em horas decimais

    hora = str(math.floor(horas_dec))

    if len(hora) == 1:

        hora = "0" + hora

    minut = (horas_dec - math.floor(horas_dec))*60

    minu = str(math.floor(minut))

    if len(minu) == 1:

        minu = "0" + minu

    segud = (minut - math.floor(minut))*60

    segu = str(int(segud))

    if len(segu) > 2:
        segu = segu[:2]

    if len(segu) == 1:

        segu = "0" + segu

    horas_dec = f"{hora}:{minu}:{segu}"

    return(horas_dec)

def main_1():
    
    URL_base = "https://pokeapi.co/api/v2/"
    
    todos_pokemons_api = requests.get(f"{URL_base}pokemon/?offset=0&limit=2000")
    
    tds_poke = todos_pokemons_api.json()
    
    qnt_total = tds_poke["count"]
    
    #print(tds_poke)
    
    dict_pokemons = {
        "ID": [],
        "Nome": [],
        "Sprite": [],
        "Type1": [],
        "Type2": [],
        "HP": [],
        "Attack":[],
        "Defense":[],
        "Special Attack":[],
        "Special Defense": [],
        "Speed":[],
        }
    
    contador = 1
    
    tempo_medio = []
    
    for pok in tds_poke["results"]:
    
        com = time.time()
    
        dict_pokemons["Nome"].append(pok["name"])#.capitalize())
    
        dados_pokemon = requests.get(f"{URL_base}pokemon/{pok["name"]}").json()
    
        dict_pokemons["ID"].append(dados_pokemon["id"])
    
        dict_pokemons["Sprite"].append(dados_pokemon["sprites"]["front_default"])
    
        tipos = dados_pokemon["types"]
    
        dict_pokemons["Type1"].append(tipos[0]["type"]["name"])
    
        if len(tipos) > 1:
            dict_pokemons["Type2"].append(tipos[1]["type"]["name"])
        else:
            dict_pokemons["Type2"].append("")
    
        stats = dados_pokemon["stats"]
    
        ordem = [
            "HP",
            "Attack",
            "Defense",
            "Special Attack",
            "Special Defense",
            "Speed",
        ]
        
        for i in range(len(stats)):
    
            dict_pokemons[ordem[i]].append(stats[i]["base_stat"])
        
    
    
        fim = time.time()
    
        tempo_med = fim - com
    
        tempo_medio.append(tempo_med)
    
        media_temp = sum(tempo_medio) / len(tempo_medio)
    
        quantos_faltam = qnt_total - contador
    
        tempo_esperado = media_temp * quantos_faltam
    
        temp_espera = horas_dec_para_relog(tempo_esperado/3600)
    
        horas = int(temp_espera[0:2])
        minutos = int(temp_espera[3:5])
        segundos = int(temp_espera[6:8])
    
        tempo_final = datetime.datetime.now() + datetime.timedelta(hours=horas,minutes=minutos,seconds=segundos)
    
        porc = round(100*contador/qnt_total,2)
        
        string_porc = f" {porc:.2f}%" 
    
        string_porc += f" | Tempo de espera médio = {temp_espera} | Espectativa de término as {tempo_final:%H:%M:%S}" 
    
        print(string_porc, end='')
        print('\b' * len(string_porc), end='', flush=True)
    
        contador += 1
    
    
    df = pd.DataFrame(dict_pokemons)
    
    
    df.to_excel("Dados Pokemon.xlsx",index=False)
    
    df.to_csv("Dados Pokemon.csv",index=False)

if __name__ == "__main__":
    
    main_1()