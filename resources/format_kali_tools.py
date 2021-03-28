import json
import os
from utils import KaliTools

"""
Sólo pruebas, las funciones se pueden implementar más adelante
pero no es nada definitivo.
"""

KT = KaliTools()
kali_tools_dict = KT.tools_dictionary
all_tools = kali_tools_dict
database = {}
for tool in all_tools:
    content = all_tools[tool]["content"]
    main = all_tools[tool]["url"]
    download = content["kali_repo_url"]
    docs = content["homepage_url"]
    database[tool.lower()] = {
            "main":main,
            "download":download,
            "documentation_page":docs
            }
new_dic = {}
def save_to_new(dic):
    for item in dic:
        homepage = dic[item]["main"]
        download = dic[item]["download"]
        docs = dic[item]["documentation_page"]
        new_dic[item] = {
                "homepage":homepage,
                "download":download,
                "docs":docs,
                "custom":{}
                }
save_to_new(database)

with open("installables.json", "w") as file:
    data = json.dumps(new_dic, indent = 4)
    file.write(data)
    file.close()
