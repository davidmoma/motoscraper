from bs4 import BeautifulSoup
import requests
import os
import random
import time


class MotoScraper:

    def __init__(self):
        # URL de partida.
        self.url = "https://www.moto-ocasion.com/" \
                   "inventory/?tipo=custom&min_precio=1&max_precio=99991"
        # Contador de motos.
        self.i = 0
        # Lista desde la que se genera el csv.
        self.motos = []
        # Lista de User-agents para rotar.
        self.AGENT_LIST = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/44.0.2403.157 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " HeadlessChrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15"
            " (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " HeadlessChrome/78.0.3904.70 Safari/537.36",
            "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/83.0.4103.97 Safari/537.36",
        ]

    def get_data(self, content: BeautifulSoup):
        """
        Esta función obtiene los nombres y valores de los campos que nos interesan y los almacena
        en las listas creadas para ello.
        :param BeautifulSoup content: objeto BeautifulSoup resultante de las páginas consultadas.
        """
        # Lista para la cabecera del fichero.
        nombre_campos = []
        # Lista con los registros.
        valor_campos = []
        # Obtenemos todas las motos de la página.
        lista_motos = content.find_all("a", {"class": "rmv_txt_drctn"})
        for entrada in lista_motos:
            self.i = self.i + 1
            # Para cada moto de la lista obtenemos el precio y la url de la ficha de la moto.
            moto_precio = entrada.find("div", {"class": "normal-price"}).getText()
            moto_url = entrada.get("href")
            moto_headers = {"User-Agent": random.choice(self.AGENT_LIST)}
            # Añadimos un retardo de 1 segundo.
            time.sleep(1)
            moto_data = requests.get(moto_url, headers=moto_headers)
            moto_soup = BeautifulSoup(moto_data.content, "html.parser")
            listado = moto_soup.find("div", {"class": "single-car-data"})
            # Recorremos la ficha de la moto.
            if len(self.motos) == 0:
                # En la primera moto, cogemos los nombres de los campos.
                campos = listado.find_all("td", {"class": "t-label"})
                for c in campos:
                    nombre_campos.append(c.getText())
                nombre_campos.append("Precio")
                # Añadimos la cabecera con los nombres de los campos (primera fila del csv).
                self.motos.append(nombre_campos)
            valores = listado.find_all("td", {"class": "t-value h6"})
            for v in valores:
                valor_campos.append(v.getText())
            valor_campos.append(moto_precio)
            # Añadimos los datos de la moto actual.
            self.motos.append(valor_campos)
            valor_campos = []
        pass

    def scrape_page(self, url: str):
        """
        Esta función extrae los datos de cada página web e invoca la función get_data para extraer
        de dichas páginas web los valores que nos interesan.
        :param str url: página web de la que extraemos los datos.
        """
        moto_headers = {"User-Agent": random.choice(self.AGENT_LIST)}
        # Añadimos un retardo de 1 segundo.
        time.sleep(1)
        r = requests.get(url, headers=moto_headers)
        soup = BeautifulSoup(r.content, "html.parser")
        # Extraemos los datos de la página que hemos recuperado.
        self.get_data(soup)
        next_page_link = soup.find("a", class_="next")
        if next_page_link is not None:
            href = next_page_link.get("href")
            # Llamada recursiva para visitar todas las páginas.
            self.scrape_page(href)
        else:
            pass

    def scrape(self):
        """
        Esta función inicia la función scrape_page con la url de partida definida al principio.
        """
        self.scrape_page(self.url)

    def data2csv(self, filename: str):
        """
        Esta función detecta si existe el directorio y el archivo en el que almacenaremos los datos.
        Si no existe los crea.
        :param str filename: nombre del archivo de salida.
        """
        path = "../dataset"
        exists = os.path.exists(path)
        if not exists:
            # Si la carpeta deseada no existe la creamos.
            os.makedirs(path)
        # Sobreescribimos en el archivo deseado, si no existe el archivo se crea.
        file = open("../dataset/" + filename, "w+")
        # Volcamos los datos en formato csv
        for i in range(len(self.motos)):
            for j in range(len(self.motos[i])):
                file.write(self.motos[i][j] + ";")
            file.write("\n")
