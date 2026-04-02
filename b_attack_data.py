import pandas as pd
import requests
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

def main_2():
    
    URL_base = "https://pokeapi.co/api/v2/"
    
    todos_pokemons_api = requests.get(f"{URL_base}move/?offset=0&limit=2000")
    
    tds_tipos = todos_pokemons_api.json()
    
    qnt_total = tds_tipos["count"]
    
    dict_pokemons = {
        "Nome": [],
        "Type": [],
        "Tipo de dano": [],
        "Accuracy":[],
        "Power": [],
        "PP": [],
        "Prioridade": [],
        "Descrição p":[],
        "Descrição c":[],
        "Chance de efeito": [],
        "Efeito": [],
        "Chance de Crit": [],
        "Drain": [],
        "Flinch": [],
        "Healing": [],
        "Min attacks": [],
        "Max attacks":[],
        "Min Turns": [],
        "Max Turns": [],
        "Chance stat": [],
        "Mudanca de stat": [],
        "Qnt de Mudança de stat": [],
        }
    
    tempo_medio = []
    
    contador = 1
    
    for pok in tds_tipos["results"]:
    
        com = time.time()
    
        dados_tipo = requests.get(f"{URL_base}move/{pok["name"]}").json()
    
        nome = dados_tipo["name"]
    
        typee = dados_tipo["type"]["name"]
    
        tipo_dano = dados_tipo["damage_class"]["name"]
    
        acuracia = dados_tipo["accuracy"]
    
        power = dados_tipo["power"]
    
        pp = dados_tipo["pp"]
    
        prioridade = dados_tipo["priority"]
    
        for i in dados_tipo["effect_entries"]:
    
            if i["language"]["name"] == "en":
    
                desc = i["short_effect"]
    
                desc_c = i["effect"]
        
        chance = dados_tipo["effect_chance"]
    
        #print(f"{URL_base}move/{pok["name"]}\n")
    
        if dados_tipo["meta"] == None:
    
            efeito = 0
            
            chance_crit = 0
    
            drain = 0
    
            flinch = 0
            
            healing = 0
    
            min_att = None
    
            max_att = None
    
            min_turns = None
    
            max_turns = None
            
            chance_stat = 0
    
        else:
    
            efeito = dados_tipo["meta"]["ailment"]["name"]
            
            chance_crit = dados_tipo["meta"]["crit_rate"]
    
            drain = dados_tipo["meta"]["drain"]
    
            flinch = dados_tipo["meta"]["flinch_chance"]
            
            healing = dados_tipo["meta"]["healing"]
    
            min_att = dados_tipo["meta"]["min_hits"]
    
            max_att = dados_tipo["meta"]["max_hits"]
    
            min_turns = dados_tipo["meta"]["min_turns"]
    
            max_turns = dados_tipo["meta"]["max_turns"]
            
            chance_stat = dados_tipo["meta"]["stat_chance"]
    
        if len(dados_tipo["stat_changes"]) < 1:
    
            qnt_m_stat = [0]
            m_stat = [""]
    
        else:
    
            qnt_m_stat = []
            m_stat = []
    
            for i in dados_tipo["stat_changes"]:
    
                qnt_m_stat.append(i["change"])
    
                m_stat.append(i["stat"]["name"])
    
        dict_pokemons["Nome"].append(nome)
        dict_pokemons["Type"].append(typee)
        dict_pokemons["Tipo de dano"].append(tipo_dano)
        dict_pokemons["Accuracy"].append(acuracia)
        dict_pokemons["Power"].append(power)
        dict_pokemons["PP"].append(pp)
        dict_pokemons["Prioridade"].append(prioridade)
        dict_pokemons["Descrição p"].append(desc)
        dict_pokemons["Descrição c"].append(desc_c)
        dict_pokemons["Chance de efeito"].append(chance)
        dict_pokemons["Efeito"].append(efeito)
        dict_pokemons["Chance de Crit"].append(chance_crit)
        dict_pokemons["Drain"].append(drain)
        dict_pokemons["Flinch"].append(flinch)
        dict_pokemons["Healing"].append(healing)
        dict_pokemons["Min attacks"].append(min_att)
        dict_pokemons["Max attacks"].append(max_att)
        dict_pokemons["Min Turns"].append(min_turns)
        dict_pokemons["Max Turns"].append(max_turns)
        dict_pokemons["Chance stat"].append(chance_stat)
        dict_pokemons["Qnt de Mudança de stat"].append(qnt_m_stat)
        dict_pokemons["Mudanca de stat"].append(m_stat)
    
    
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
    
    df.to_csv("Attacks.csv",index=False)

if __name__ == "__main__":
    
    main_2()