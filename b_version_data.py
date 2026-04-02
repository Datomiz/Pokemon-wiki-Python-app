import pandas as pd
import requests

def main_6():
    
    URL_base = "https://pokeapi.co/api/v2/"
    
    todos_pokemons_api = requests.get(f"{URL_base}version-group/?offset=0&limit=2000")
    
    tds_tipos = todos_pokemons_api.json()
    
    
    dict_pokemons = {
        "Jogo": [],
        "Gen": [],
        }
    
    dict_traduz_gen = {
                    "generation-i":"Gen 1",
                    "generation-ii":"Gen 2",
                    "generation-iii":"Gen 3",
                    "generation-iv":"Gen 4",
                    "generation-v":"Gen 5" ,
                    "generation-vi":"Gen 6" ,
                    "generation-vii":"Gen 7" ,
                    "generation-viii":"Gen 8" ,
                    "generation-ix":"Gen 9" ,
                }
    
    contador = 1
    
    
    for pok in tds_tipos["results"]:
    
        dados_jogo = requests.get(pok["url"]).json()
    
        gen = dict_traduz_gen[dados_jogo["generation"]["name"]]
    
        dict_pokemons["Jogo"].append(pok["name"])
        dict_pokemons["Gen"].append(gen)
    
    
    df = pd.DataFrame(dict_pokemons)
    
    df.to_csv("Jogos gen.csv",index=False)

if __name__ == "__main__":
    
    main_6()