import requests
from bs4 import BeautifulSoup as BS
import json

HEADERS = {'User-Agent': 'curl/7.38.0'}
PARSER = "html.parser"

def get_tool_content(url):
    response = requests.get(url, headers = HEADERS)
    soup = BS(response.text, PARSER)
    page_title = soup.title.text

    # Obtiene los enlaces a la página de la herramienta,
    # y la página del repositorio de kali.
    # Al igual que la descripción.

    wrapper = soup.find("div", {"class":"wpb_wrapper"})
    references = wrapper.find_all("a")

    content_dictionary={}

    if len(references) > 1:
        homepage = references[0]
        kali_repo = references[1]
        try:
            kali_repo_url = kali_repo["href"]
            homepage_url = homepage["href"]
        except:
            homepage_url = homepage["hef"]
    else:
        kali_repo = references[0]
        kali_repo_url = kali_repo["href"]
        homepage_url = None

    description = soup.find("div", {"class":"l-section-h"})
    try:
        description = description.p.text
    except:
        description = f"Visita {url} para leer la descripción"

    content_dictionary = {"homepage_url":homepage_url, "kali_repo_url":kali_repo_url,"description":description}
    return content_dictionary


def get_kali_tools(url):
    # Obtiene los enlaces a las herramientas de kali.
    response = requests.get(url, headers = HEADERS)
    soup=BS(response.text, PARSER)
    containers = soup.find_all("ul", {"class":"lcp_catlist"})
    database = {}
    # Obtiene las herramientas por cada gategoría
    for index, section in enumerate(containers):
        section_title = section.parent.h5.text
        tools = section.find_all("li")
        database[section_title] = {}
        print(f"Obteniendo información de la sección: {section_title} ({index}/{len(containers)})     ...", end="\r")
        for tool in tools:
            title = tool.a["title"]
            url = tool.a["href"]
            # A partir del enlace de la herramienta, obtiene el contenido breve de
            # la página de la herramienta.
            tool_content = get_tool_content(url)
            database[section_title][title] = {"url":url, "content":tool_content}
    return database

database = get_kali_tools("https://tools.kali.org/tools-listing")
print()


with open("kali_tools.json", "w") as file:
    json.dump(database, file)
    file.close()
