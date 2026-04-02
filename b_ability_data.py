import pandas as pd
import requests

def main_3():
    
    URL_base = "https://pokeapi.co/api/v2/"
    
    todos_pokemons_api = requests.get(f"{URL_base}ability/?offset=0&limit=2000")
    
    tds_tipos = todos_pokemons_api.json()
    
    dict_pokemons = {
        "Habilidade": [],
        "Efeito": [],
        }
    
    #contador = 1
    
    for pok in tds_tipos["results"]:
    
        dados_tipo = requests.get(f"{URL_base}ability/{pok["name"]}").json()
    
        for i in dados_tipo["effect_entries"]:
    
            if i["language"]["name"] == "en":
    
                efeito = i["effect"]
       
        dict_pokemons["Habilidade"].append(pok["name"])
        dict_pokemons["Efeito"].append(efeito)
    
    
    df = pd.DataFrame(dict_pokemons)
    
    df.to_csv("Habilidades.csv",index=False)


if __name__ == "__main__":
    
    main_3()