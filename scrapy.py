# https://www.analyticsvidhya.com/blog/2017/07/web-scraping-in-python-using-scrapy/
# https://www.digitalocean.com/community/tutorials/como-fazer-crawling-em-uma-pagina-web-com-scrapy-e-python-3-pt
# http://pythonclub.com.br/material-do-tutorial-web-scraping-na-nuvem.html
import scrapy
import re
import json


class PokemonScrapper(scrapy.Spider):
    name = "pokemon_scrapper"
    # domain = 'https://bulbapedia.bulbagarden.net'
    start_urls = ["https://www.serebii.net/pokedex/001.shtml"]
    for i in range(1, 152):
        print(str(i).zfill(3))

    def parse(self, response):
        total_pages = 152  # passo o total de páginas a serem percorridas
        for page in range(1, total_pages):
            url = "https://www.serebii.net/pokedex/" + str(page).zfill(
                3
            ) + ".shtml"  # formata a url com a página atual (mantendo o formato 001 do número na url)
            yield scrapy.Request(url, callback=self.parse_page)
        # Passa a primeira página
        yield from self.parse_page(self, response)

    def parse_page(self, response):

        dextable = response.css('.dextable')

        #Linha 1
        tr = dextable[1].css("tr")[1]
        #Nome
        td = tr.css(".fooinfo")[0]
        nome = td.css("::text")

        #Número
        td = tr.css(".fooinfo")[2]
        numero = td.css("::text")

        #Tipo
        td = tr.css(".cen")
        imgs = td.css("img::attr(src)")
        img_name = []
        for img in imgs:
            img_name.append(
                re.split(r'(\w+\.)', img.get())[1].replace('.', ''))

        #Linha 2
        tr = dextable[1].css("tr")

        #Tamanho
        td = tr.css(".fooinfo")[4]
        tamanho = td.css("::text").getall()
        tamanho_pes = tamanho[0]
        tamanho_metros = tamanho[1].replace("\t",
                                            "").replace("\r",
                                                        "").replace("\n", "")

        #Peso
        td = tr.css(".fooinfo")[5]
        peso = td.css("::text").getall()
        peso_lbs = peso[0]
        peso_kgs = peso[1].replace("\t", "").replace("\r",
                                                     "").replace("\n", "")

        #Tipo de dano recebido
        tr = dextable[3].css("tr")
        tipos_dano = []
        for i in range(15):
            td_tipo = tr.css(".footype")[i]
            td_valor = tr.css(".footype")[i + 15]
            tipo_dano = td_tipo.css("a::attr(href)").get()
            tipo_dano = re.split(r'(\w+\.)', tipo_dano)[1].replace('.', '')
            valor_dano = td_valor.css("::text").get()
            tipos_dano.append({tipo_dano: valor_dano})

        #Próxima evolução
        tr = dextable[4].css("tr")
        proxima_evolucao = ""
        tamanho_tr = len(tr.css(".pkmn"))
        if(numero == "#151" or numero == "#150"):
            print(numero, tamanho_tr)
        for i in range(0, 3):
            if((i == 2 and tamanho_tr == 4)or (i == 1 and tamanho_tr == 2)):
                proxima_evolucao = "Não possui"
                break
            td = tr.css(".pkmn")[i]
            img_url = td.css("a::attr(href)").get()
            proxima_evolucao = re.split(r'(\w+\.)',
                                        img_url)[1].replace('.', '')

            if (int(proxima_evolucao) > int(numero.get().replace("#", ""))):
                break
            else:
                proxima_evolucao = "Não possui"

        infos = {
            "numero": numero.get(),
            "nome": nome.get(),
            "proxima_evolucao": proxima_evolucao if proxima_evolucao == "Não possui" else "#" + proxima_evolucao,
            "tamanho_pes": tamanho_pes,
            "tamanho_metros": tamanho_metros,
            "peso_lbs": peso_lbs,
            "peso_kgs": peso_kgs,
            "tipo": img_name,
            "tipos_dano": tipos_dano
        }
        # yield infos
        with open('pokemons_info.txt', 'a', newline='') as arquivo:
            arquivo.write(json.dumps(infos, ensure_ascii=False) + '\n')
        print('\n\n')


# scrapy runspider main.py


