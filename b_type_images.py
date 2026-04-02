import pandas as pd
import requests

def main_5():
    
    URL_base = "https://pokeapi.co/api/v2/"
    
    todos_pokemons_api = requests.get(f"{URL_base}type/?offset=0&limit=2000")
    
    tds_tipos = todos_pokemons_api.json()
    
    
    
    dict_pokemons = {
        "Tipo": [],
        "Imagem": [],
        "Relations": [],
        }
    
    #contador = 1
    
    
    for pok in tds_tipos["results"]:
    
        dados_tipo = requests.get(f"{URL_base}type/{pok["name"]}").json()
    
        sprite_final = ""
    
        sprites = dados_tipo["sprites"]
    
        for gen in sprites:
    
            for game in sprites[gen]:
    
                for url in sprites[gen][game].values():
    
                    if url != None:
    
                        sprite_final = url
                        break
        
        weak = {}
    
    
        for i in dados_tipo["damage_relations"]["double_damage_from"]:
    
            weak[i["name"]] = 2
    
        for i in dados_tipo["damage_relations"]["half_damage_from"]:
    
            weak[i["name"]] = 1/2
    
        for i in dados_tipo["damage_relations"]["no_damage_from"]:
    
            weak[i["name"]] = 0
       
        #print(sprite_final)
    
        dict_pokemons["Tipo"].append(pok["name"])
        dict_pokemons["Imagem"].append(sprite_final)
        dict_pokemons["Relations"].append(weak)
    
    
    df = pd.DataFrame(dict_pokemons)
    
    df.to_csv("Imagens tipos.csv",index=False)

if __name__ == "__main__":
    
    main_5()
