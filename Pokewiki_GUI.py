import customtkinter as ctk
import csv
import requests
from PIL import Image#, ImageTK
from io import BytesIO
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import sys

PAGE_SIZE = 20

ctk.set_appearance_mode("dark")



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pokedex")
        self.geometry("750x550")

        self.data = self.load_csv("Dados Pokemon.csv")
        self.data_tipos = self.load_csv("Imagens tipos.csv")
        self.data_gen = self.load_csv("Jogos gen.csv")
        self.data_att = self.load_csv("Attacks.csv")
        self.data_hab = self.load_csv("Habilidades.csv")
        self.data_ftex = self.load_csv("Flavor text.csv")



        self.filtered_data = self.data.copy()
        self.image_cache = {}
        self.current_page = 0


        self.my_font = ctk.CTkFont(
            family="Arial",
            size=16,
            weight="bold"
        )

        self.my_fontM = ctk.CTkFont(
            family="Arial",
            size=22,
            weight="bold"
        )


        self.dict_tipos = {}
        self.dict_tipos_r = {}

        for i in self.data_tipos:
            self.dict_tipos[i["Tipo"]] = i["Imagem"]
            self.dict_tipos_r[i["Tipo"]] = i["Relations"]

        self.dict_gens = {}

        for i in self.data_gen:
            self.dict_gens[i["Jogo"]] = i["Gen"]

        self.dict_atts = {}

        for i in self.data_att:

            self.dict_atts[i["Nome"]] = i

        self.dict_hab = {}

        for i in self.data_hab:

            self.dict_hab[i["Habilidade"]] = i["Efeito"]

        self.dick_ftext = {}

        for i in self.data_ftex:

            self.dick_ftext[i["Pokemon"]] = dict(eval(i["Text dict"]))

        # ---------- SEARCH ----------
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search by name...",
            textvariable=self.search_var
        )
        self.search_entry.pack(fill="x", padx=10, pady=(10, 5))
        self.search_entry.bind("<KeyRelease>", self.apply_filter)

        # ---------- SCROLLABLE ----------
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # ---------- PAGINATION ----------
        nav = ctk.CTkFrame(self)
        nav.pack(fill="x", padx=10, pady=5)

        self.prev_btn = ctk.CTkButton(nav, text="◀ Prev", command=self.prev_page)
        self.prev_btn.pack(side="left", padx=5)

        self.page_label = ctk.CTkLabel(nav, text="")
        self.page_label.pack(side="left", padx=10)

        self.next_btn = ctk.CTkButton(nav, text="Next ▶", command=self.next_page)
        self.next_btn.pack(side="left", padx=5)

        self.render_page()

        self.protocol("WM_DELETE_WINDOW", self._quit)

    def _quit(self):
        self.quit()
        self.destroy() 
        sys.exit()

    # ---------- DATA ----------
    def load_csv(self, path):
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # ---------- FILTER ----------
    def apply_filter(self, event=None):
        if hasattr(self, "_search_job"):
            self.after_cancel(self._search_job)

        self._search_job = self.after(300, self._do_filter)

    def _do_filter(self):
        query = self.search_var.get().lower().strip()

        self.filtered_data = [
            item for item in self.data
            if query in item["Nome"].lower()
        ] if query else self.data

        self.current_page = 0
        self.render_page()


    # ---------- PAGINATION ----------
    def render_page(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        start = self.current_page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = self.filtered_data[start:end]

        for row, item in enumerate(page_items):
            self.add_row(row, item)

        total_pages = max(1, (len(self.filtered_data) - 1) // PAGE_SIZE + 1)
        self.page_label.configure(
            text=f"Page {self.current_page + 1} / {total_pages}"
        )

        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(
            state="normal" if end < len(self.filtered_data) else "disabled"
        )

    def next_page(self):
        self.current_page += 1
        self.render_page()

    def prev_page(self):
        self.current_page -= 1
        self.render_page()

    # ---------- ROW ----------
    def add_row(self, row, item):

        

        img_label = ctk.CTkLabel(self.scroll_frame, text="")
        img_label.grid(row=row, column=0, padx=10, pady=6)

        img = self.get_image_async(item["Sprite"], img_label,(60,60))

        ctk.CTkLabel(self.scroll_frame, text=item["Nome"].capitalize(), anchor="w",font = self.my_font).grid(
            row=row, column=1, padx=10, pady=6
        )


        img_label2 = ctk.CTkLabel(self.scroll_frame, text="",width=1)
        img_label2.grid(row=row, column=2, padx=10, pady=6)
        
        url_t_1 = self.dict_tipos[item["Type1"]]

        t_img = self.get_image_async( url_t_1, img_label2,(90,20))

       
        img_label3 = ctk.CTkLabel(self.scroll_frame, text="",width=1)
        img_label3.grid(row=row, column=3, padx=10, pady=6)
        
        if item["Type2"] != "":

            url_t_2 = self.dict_tipos[item["Type2"]]

            t_img2 = self.get_image_async( url_t_2, img_label3,(90,20))

        ctk.CTkButton(
            self.scroll_frame,
            text="More info",
            width=100,
            command=lambda i=item: self.show_info(i)
        ).grid(row=row, column=4, padx=10)

    # ---------- IMAGE CACHE ----------
    
    def get_image_async(self, url, label,rez:tuple):
        if url in self.image_cache:
            label.configure(image=self.image_cache[url])
            return

        def task():
            try:
                response = requests.get(url, timeout=5)
                img = Image.open(BytesIO(response.content))

                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                
                img = img.resize(rez,resample=Image.Resampling.LANCZOS)
                
                
                ctk_img = ctk.CTkImage(img, size=rez)
                self.image_cache[url] = ctk_img

                # UI update MUST be on main thread
                self.after(0, lambda: label.configure(image=ctk_img))
            except Exception:
                pass

        threading.Thread(target=task, daemon=True).start()

    def show_info_att(self,GUI_i,dados_att):
        

        GUI_i.attributes('-topmost', 'false')

        GUI_a = ctk.CTkToplevel(self)
        GUI_a.title(f'Info {dados_att["Nome"]}')
        GUI_a.geometry('740x900')

        GUI_a.attributes('-topmost', 'true')

        ctk.CTkLabel(GUI_a, text=dados_att["Nome"].capitalize(), anchor="w",font = self.my_fontM).grid(
            row=0, column=0, padx=10,columnspan = 5,
        )

        ctk.CTkLabel(GUI_a, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=1, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        desc = dados_att["Descrição c"]

        contador = 0

        for i in range(len(desc)):

            if contador > 70:

                desc = desc[0:i] + "\n" + desc[i:]

                contador = 0
        
            contador += 1


        ctk.CTkLabel(GUI_a, text=desc, anchor="w",font = self.my_font).grid(
            row=2, column=0, padx=10,columnspan = 5,
        )

        ctk.CTkLabel(GUI_a, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=3, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        ctk.CTkLabel(GUI_a, text="Power", anchor="w",font = self.my_fontM).grid(
            row=4, column=0, padx=10, pady=6,
        )

        power = dados_att["Power"]

        if power != "":

            power = int(float(power))

        ctk.CTkLabel(GUI_a, text=power, anchor="w",font = self.my_font).grid(
        row=5, column=0, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="Accuracy", anchor="w",font = self.my_fontM).grid(
            row=4, column=1, padx=10, pady=6,
        )

        acc = dados_att["Accuracy"]

        if acc != "":

            acc = int(float(acc))

        ctk.CTkLabel(GUI_a, text=acc, anchor="w",font = self.my_font).grid(
        row=5, column=1, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="Type", anchor="w",font = self.my_fontM).grid(
            row=4, column=3, padx=10, pady=6,
        )

        img_label4 = ctk.CTkLabel(GUI_a, text="",width=1)
        img_label4.grid(row=5, column=3, padx=10, pady=6)
        
        url_t_4 = self.dict_tipos[dados_att["Type"]]

        t_img3 = self.get_image_async( url_t_4, img_label4,(90,20))

        ctk.CTkLabel(GUI_a, text="PP", anchor="w",font = self.my_fontM).grid(
            row=4, column=2, padx=10, pady=6,
        )

        pp = dados_att["PP"]

        if pp != "":

            pp = int(float(pp))

        ctk.CTkLabel(GUI_a, text=pp, anchor="w",font = self.my_font).grid(
        row=5, column=2, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=6, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        ctk.CTkLabel(GUI_a, text="Att/Sp.Att", anchor="w",font = self.my_fontM).grid(
            row=7, column=0, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Tipo de dano"], anchor="w",font = self.my_font).grid(
        row=8, column=0, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="Priority", anchor="w",font = self.my_fontM).grid(
            row=7, column=1, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Prioridade"], anchor="w",font = self.my_font).grid(
        row=8, column=1, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="Effect", anchor="w",font = self.my_fontM).grid(
            row=7, column=2, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Efeito"], anchor="w",font = self.my_font).grid(
        row=8, column=2, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="%Efeito", anchor="w",font = self.my_fontM).grid(
            row=7, column=3, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Chance de efeito"], anchor="w",font = self.my_font).grid(
        row=8, column=3, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=9, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        ctk.CTkLabel(GUI_a, text="%Flinch", anchor="w",font = self.my_fontM).grid(
            row=10, column=0, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Flinch"], anchor="w",font = self.my_font).grid(
        row=11, column=0, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="%Crit", anchor="w",font = self.my_fontM).grid(
            row=10, column=1, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Chance de Crit"], anchor="w",font = self.my_font).grid(
        row=11, column=1, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="%Drain", anchor="w",font = self.my_fontM).grid(
            row=10, column=2, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Drain"], anchor="w",font = self.my_font).grid(
        row=11, column=2, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="%Heal", anchor="w",font = self.my_fontM).grid(
            row=10, column=3, padx=10, pady=6,
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Healing"], anchor="w",font = self.my_font).grid(
        row=11, column=3, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=12, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        ctk.CTkLabel(GUI_a, text="Min Att", anchor="w",font = self.my_fontM).grid(
            row=13, column=0, padx=10, pady=6,
        )

        mina = dados_att["Min attacks"]

        if mina != "":

            mina = int(float(mina))

        ctk.CTkLabel(GUI_a, text=mina, anchor="w",font = self.my_font).grid(
        row=14, column=0, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="Max Att", anchor="w",font = self.my_fontM).grid(
            row=13, column=1, padx=10, pady=6,
        )

        maxa = dados_att["Max attacks"]

        if maxa != "":

            maxa = int(float(maxa))

        ctk.CTkLabel(GUI_a, text=maxa, anchor="w",font = self.my_font).grid(
        row=14, column=1, padx=10, pady=6
        )


        ctk.CTkLabel(GUI_a, text="Min Turns", anchor="w",font = self.my_fontM).grid(
            row=13, column=2, padx=10, pady=6,
        )

        mint = dados_att["Min Turns"]

        if mint != "":

            mint = int(float(mint))

        ctk.CTkLabel(GUI_a, text=mint, anchor="w",font = self.my_font).grid(
        row=14, column=2, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="Max Turns", anchor="w",font = self.my_fontM).grid(
            row=13, column=3, padx=10, pady=6,
        )

        maxt = dados_att["Max Turns"]

        if maxt != "":

            maxt = int(float(maxt))

        ctk.CTkLabel(GUI_a, text=maxt, anchor="w",font = self.my_font).grid(
        row=14, column=3, padx=10, pady=6
        )

        ctk.CTkLabel(GUI_a, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=15, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        ctk.CTkLabel(GUI_a, text="Chance de Stat", anchor="w",font = self.my_fontM).grid(
            row=16, column=0, padx=10, pady=6, columnspan = 2
        )

        ctk.CTkLabel(GUI_a, text=dados_att["Chance stat"], anchor="w",font = self.my_font).grid(
        row=17, column=0, padx=10, pady=6, columnspan = 2
        )

        ctk.CTkLabel(GUI_a, text="+-Stat", anchor="w",font = self.my_fontM).grid(
            row=16, column=2, padx=10, pady=6
        )

        dados_att["Mudanca de stat"] = list(eval(dados_att["Mudanca de stat"]))

        maxi = 17

        for i in range(len(dados_att["Mudanca de stat"])):

            ctk.CTkLabel(GUI_a, text=dados_att["Mudanca de stat"][i], anchor="w",font = self.my_font).grid(
            row=17 + i, column=2, padx=10, pady=6
            )

            if maxi < 17 + i:
                maxi = 17+i

        ctk.CTkLabel(GUI_a, text="Qnt Stat", anchor="w",font = self.my_fontM).grid(
            row=16, column=3, padx=10, pady=6
        )

        dados_att["Qnt de Mudança de stat"] = list(eval(dados_att["Qnt de Mudança de stat"]))

        for i in range(len(dados_att["Qnt de Mudança de stat"])):

            ctk.CTkLabel(GUI_a, text=dados_att["Qnt de Mudança de stat"][i], anchor="w",font = self.my_font).grid(
            row=17 + i, column=3, padx=10, pady=6
            )

            if maxi < 17 + i:
                maxi = 17+i


        ctk.CTkLabel(GUI_a, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=maxi+1, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________
        

    def info_ablidade(self,GUI_i,hab:str):

        GUI_h = ctk.CTkToplevel(self)
        GUI_h.title(f'Info {hab.capitalize()}')
        GUI_h.geometry('740x400')

        GUI_i.attributes('-topmost', 'false')
        GUI_h.attributes('-topmost', 'true')

        ctk.CTkLabel(GUI_h, text=hab.capitalize(), anchor="w",font = self.my_fontM).grid(
            row=0, column=0, padx=10,columnspan = 5,
        )

        ctk.CTkLabel(GUI_h, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=1, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        desc = self.dict_hab[hab]

        contador = 0

        for i in range(len(desc)):

            if contador > 70:

                desc = desc[0:i] + "\n" + desc[i:]

                contador = 0
        
            contador += 1


        ctk.CTkLabel(GUI_h, text=desc, anchor="w",font = self.my_font).grid(
            row=2, column=0, padx=10,columnspan = 5,
        )

        ctk.CTkLabel(GUI_h, text="_" * 80, anchor="w",font = self.my_font).grid(
        row=3, column=0, padx=10,columnspan = 5
        )
        #_______________________________________________________________________

        



        

    def show_info(self, item):

        GUI_i = ctk.CTkToplevel(self)
        GUI_i.title(f'Info {item["Nome"]}')
        GUI_i.geometry('1500x650')

        GUI_i.attributes('-topmost', 'true')

        URL_base = "https://pokeapi.co/api/v2/"

        dados_pokemon = requests.get(f"{URL_base}pokemon/{item["Nome"]}").json()

        sprite_f = item["Sprite"]
        try:
            sprite_f = dados_pokemon["sprites"]["other"]["official-artwork"]["front_default"]
        except:
            pass

            sprites = dados_pokemon["sprites"]["versions"]

            for gen in sprites:

                for game in sprites[gen]:

                    if "icon" not in game:

                        for sp in sprites[gen][game]:

                            if "shiny"not in sp and "front" in sp and sprites[gen][game][sp] != None:

                                sprite_f = sprites[gen][game][sp]

        dict_EV = {}

        for i in dados_pokemon["stats"]:

            if i["effort"] != 0:

                dict_EV[i["stat"]["name"]] = i["effort"]
        
        

        # print(item)

        img_label = ctk.CTkLabel(GUI_i, text="")
        img_label.grid(row=0, column=0, padx=10, pady=6,columnspan = 2)

        img2 = self.get_image_async(sprite_f, img_label,(200,200))

        ctk.CTkLabel(GUI_i, text=item["Nome"].capitalize(), anchor="w",font = self.my_fontM).grid(
            row=1, column=0, padx=10, pady=6,columnspan = 2,
        )

        img_label2 = ctk.CTkLabel(GUI_i, text="",width=1)
        img_label2.grid(row=2, column=0, padx=10, pady=6)

        relcao1 = dict(eval(self.dict_tipos_r[item["Type1"]]))

        if item["Type2"] != "":

            relcao2 = dict(eval(self.dict_tipos_r[item["Type2"]]))
        
        else:

            relcao2 = {}
        
        relacao_f = {}

        for i in relcao1:

            relacao_f[i] = relcao1[i]
        
        for i in relcao2:

            if i in relacao_f:

                relacao_f[i] = relacao_f[i] * relcao2[i]
            
            else:

                relacao_f[i] = relcao2[i]
        
        


        
        url_t_1 = self.dict_tipos[item["Type1"]]

        t_img = self.get_image_async( url_t_1, img_label2,(90,20))

       
        img_label3 = ctk.CTkLabel(GUI_i, text="",width=1)
        img_label3.grid(row=2, column=1, padx=10, pady=6)
        
        if item["Type2"] != "":

            url_t_2 = self.dict_tipos[item["Type2"]]

            t_img2 = self.get_image_async( url_t_2, img_label3,(90,20))

        ordem = [
            "HP",
            "Attack",
            "Defense",
            "Special Attack",
            "Special Defense",
            "Speed",
        ]

        values = []

        for i in ordem:

            values.append(int(item[i]))
        
        fig = plt.Figure(figsize=(4.5, 2.8), dpi=100)
        ax = fig.add_subplot(111)

        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        norm = mcolors.Normalize(vmin=50, vmax=180)
        cmap = plt.get_cmap("viridis")
        colors = cmap(norm(values))

        bars = ax.barh(ordem, values, color=colors)
        ax.set_xlim(0, 250)
        ax.set_xlabel("Value")

        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")

        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")

        ax.get_xaxis().set_visible(False)

        ax.get_xaxis().set_visible(False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.invert_yaxis()

        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 3,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)}",
                va="center",
                fontsize=9,
                color = "white"
            )

        fig.tight_layout()

        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        canvas = FigureCanvasTkAgg(fig, master=GUI_i)
        canvas.draw()
        canvas.get_tk_widget()#.pack(fill="both", expand=False)

        widget = canvas.get_tk_widget()
        widget.configure(
            bg=GUI_i._apply_appearance_mode(GUI_i._fg_color)
        )
        #widget.pack(fill="both", expand=False)
        widget.grid(row=0,column=2,columnspan = 2, padx=10, pady=5)


        ctk.CTkLabel(GUI_i, text="Abilities:", anchor="w",font = self.my_fontM).grid(
                row=3, column=0, padx=10, pady=6,columnspan = 2
            )


        scroll_frame_ab = ctk.CTkScrollableFrame(GUI_i,width= 250,height=1)
        scroll_frame_ab.grid(row=4,column = 0, padx=10, pady=5,columnspan = 2)

        lista_ab = []

        for i in dados_pokemon["abilities"]:

            nome = i["ability"]["name"]

            if i["is_hidden"]:

                nome += " (Hidden)"
            
            lista_ab.append(nome)

        for i in range(len(lista_ab)):

            ctk.CTkLabel(scroll_frame_ab, text=lista_ab[i].capitalize(), anchor="w",font = self.my_font).grid(
                row=i, column=0, padx=10, pady=6,
            )

            lista_ab[i] = lista_ab[i].replace(" (Hidden)","")

            ctk.CTkButton(
                    scroll_frame_ab,
                    text="...",
                    width=50,
                    command=lambda x=i: self.info_ablidade(GUI_i,lista_ab[x] )
                ).grid(row=i, column=1, padx=10)

        scroll_frame_at = ctk.CTkScrollableFrame(GUI_i,width= 600,height=200)
        scroll_frame_at.grid(row=3,column = 2, padx=10, pady=5,rowspan = 2,columnspan = 2)

        def atualizar_moves(choice):
            
            for widget in scroll_frame_at.winfo_children():
                widget.destroy()
            

            gen_o = choice

            dict_atacks = {}

            for at in dados_pokemon["moves"]:

                nome = at["move"]["name"]

                for i in at["version_group_details"]:

                    nivel = i["level_learned_at"]

                    jogo = i["version_group"]["name"]

                    gen = self.dict_gens[jogo]

                    if gen == gen_o and nivel != 0:

                        dict_atacks[nome] = nivel 
            
                
            
            dict_atacks = dict(sorted(dict_atacks.items(), key=lambda item: item[1]))

            #print(dict_atacks)

            ctk.CTkLabel(scroll_frame_at, text="Attack", anchor="w",font = self.my_font).grid(
            row=0, column=0, padx=10, pady=6
            )

            ctk.CTkLabel(scroll_frame_at, text="Lv", anchor="w",font = self.my_font).grid(
            row=0, column=1, padx=10, pady=6
            )

            ctk.CTkLabel(scroll_frame_at, text="Power", anchor="w",font = self.my_font).grid(
            row=0, column=2, padx=10, pady=6
            )
            
            ctk.CTkLabel(scroll_frame_at, text="Acc", anchor="w",font = self.my_font).grid(
            row=0, column=3, padx=10, pady=6
            )

            ctk.CTkLabel(scroll_frame_at, text="Type", anchor="w",font = self.my_font).grid(
            row=0, column=4, padx=10, pady=6
            )

            ctk.CTkLabel(scroll_frame_at, text="At/Sp", anchor="w",font = self.my_font).grid(
            row=0, column=5, padx=10, pady=6
            )

            ctk.CTkLabel(scroll_frame_at, text="Info", anchor="w",font = self.my_font).grid(
            row=0, column=6, padx=10, pady=6
            )

            counter = 1

            for i in dict_atacks:

                ctk.CTkLabel(scroll_frame_at, text=i.capitalize(), anchor="w",font = self.my_font).grid(
                row=counter, column=0, padx=10, pady=6
                )

                ctk.CTkLabel(scroll_frame_at, text=dict_atacks[i], anchor="w",font = self.my_font).grid(
                row=counter, column=1, padx=10, pady=6
                )

                power = self.dict_atts[i]["Power"]

                if power != "":

                    power = int(float(power))

                ctk.CTkLabel(scroll_frame_at, text=power, anchor="w",font = self.my_font).grid(
                row=counter, column=2, padx=10, pady=6
                )

                acc = self.dict_atts[i]["Accuracy"]

                if acc != "":

                    acc = int(float(acc))

                ctk.CTkLabel(scroll_frame_at, text=acc, anchor="w",font = self.my_font).grid(
                row=counter, column=3, padx=10, pady=6
                )

                img_label3 = ctk.CTkLabel(scroll_frame_at, text="",width=1)
                img_label3.grid(row=counter, column=4, padx=10, pady=6)
                
                url_t_3 = self.dict_tipos[self.dict_atts[i]["Type"]]

                t_img2 = self.get_image_async( url_t_3, img_label3,(90,20))


                ctk.CTkLabel(scroll_frame_at, text=self.dict_atts[i]["Tipo de dano"].capitalize(), anchor="w",font = self.my_font).grid(
                row=counter, column=5, padx=10, pady=6
                )

                ctk.CTkButton(
                    scroll_frame_at,
                    text="...",
                    width=50,
                    command=lambda x=i: self.show_info_att(GUI_i,self.dict_atts[x])
                ).grid(row=counter, column=6, padx=10)



                counter += 1


        lista_gens = [
            "Gen 1",
            "Gen 2",
            "Gen 3",
            "Gen 4",
            "Gen 5",
            "Gen 6",
            "Gen 7",
            "Gen 8",
            "Gen 9",
            ][::-1]
        
        atualizar_moves("Gen 9")


        geracao = ctk.CTkComboBox(GUI_i, values = lista_gens,command=atualizar_moves)
        geracao.grid(row=2, column=2, padx=10, pady=6,columnspan = 2)

        ctk.CTkLabel(GUI_i, text="Moves:", anchor="w",font = self.my_fontM).grid(
                row=1, column=2, padx=10, pady=6,columnspan = 2
            )
        
        #print(relacao_f)


        frame_rel = ctk.CTkFrame(GUI_i,width=300,height=300)
        frame_rel.grid(
            row = 0,column = 4, padx=10, pady=6
        )

        colunas = {
            "4x":4,
            "2x":2,
            "1/2":0.5,
            "1/4":0.25,
            "0x": 0,
        }

        contador = 0

        for i in colunas:
            
            ctk.CTkLabel(frame_rel, text=i, anchor="w",font = self.my_fontM).grid(
                row=0, column=contador, padx=10, pady=6
            )

            contador_r = 1

            for j in relacao_f:
                
                if relacao_f[j] == colunas[i]:

                    # ctk.CTkLabel(frame_rel, text=j, anchor="w",font = self.my_fontM).grid(
                    #     row=contador_r, column=contador, padx=10, pady=6
                    # )

                    img_label3 = ctk.CTkLabel(frame_rel, text="",width=1)
                    img_label3.grid(row=contador_r, column=contador, padx=10, pady=6)
                    
                    url_t_3 = self.dict_tipos[j]

                    t_img2 = self.get_image_async( url_t_3, img_label3,(90,20))

                    contador_r += 1

            contador += 1



        f_text = self.dick_ftext[item["Nome"]]

        # ctk.CTkLabel(GUI_i, text="Game:", anchor="w",font = self.my_fontM).grid(
        #         row=2, column=4, padx=10, pady=6
        #     )


        dict_stat = {
            "hp":"HP",
            "attack":"Att",
            "defense":"Def",
            "special-attack":"Sp Att",
            "special-defense":"Sp Def",
            "speed":"Spd",
        }

        frame_EV = ctk.CTkFrame(GUI_i,width=100,height=100)
        frame_EV .grid(
            row = 1,column = 4, padx=10, pady=6,rowspan = 2
        )

        ctk.CTkLabel(frame_EV, text="EV:", anchor="w",font = self.my_fontM).grid(
                row=0, column=0, padx=10, pady=6,rowspan = 2
            )

        contador = 1

        for i in dict_EV:
            ctk.CTkLabel(frame_EV, text=dict_stat[i], anchor="w",font = self.my_fontM).grid(
                row=0, column=contador, padx=10, pady=6
            )

            ctk.CTkLabel(frame_EV, text=dict_EV[i], anchor="w",font = self.my_fontM).grid(
                row=1, column=contador, padx=10, pady=6
            )

            contador += 1



        frame_f_text = ctk.CTkFrame(GUI_i,width=300,height=300)
        frame_f_text.grid(
            row = 4,column = 4, padx=10, pady=6,rowspan = 2
        )
        
        def flavor_text(choice):

            for widget in frame_f_text.winfo_children():
                widget.destroy()

            ctk.CTkLabel(frame_f_text, text="Flavor Text:", anchor="w",font = self.my_fontM).grid(
                row=0, column=0, padx=10, pady=6
            )

            texto_f = f_text[choice]

            contador = 0
            if "\n" not in texto_f:
                for i in range(len(texto_f)):

                    if contador > 40:

                        texto_f = texto_f[0:i] + "\n" + texto_f[i:]

                        contador = 0
                
                    contador += 1

            

            ctk.CTkLabel(frame_f_text, text=texto_f , anchor="w",font = self.my_fontM).grid(
                row=1, column=0, padx=10, pady=6
            )
        
        flavor_text(list(f_text.keys())[-1])

        jogo = ctk.CTkComboBox(GUI_i, values = list(f_text.keys())[::-1],command=flavor_text)
        jogo.grid(row=3, column=4, padx=10, pady=6)

        

        





        


if __name__ == "__main__":
    app = App()
    app.mainloop()
