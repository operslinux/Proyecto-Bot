import re
import json


"""
Este módulo debe procesar los mensajes detectados como requisitos de ayuda
junta información registrada en el directorio 'recursos', falta pulir un par
de detalles y añadir una función para añadir recursos a las bases de datos,
también una función para dar formato a los recursos, para enviarlos correctamente
al usuario.
"""


# Cargar la base de datos de los recursos instalables (programas, sistemas operativos,
# herramientas, lenguajes de programación, etc.)
installables = json.loads(open("resources/installables.json","r").read())
#installables_list = [item.lower() for item in installables]
installables_list = [item for item in installables]

# Cargar la base de datos de recursos personalizados (cualquier tipo de recurso).
custom_contents = json.loads(open("resources/custom_contents.json","r").read())

# Palabras clave donde alguien dice ser iniciante.
beginner_keywords = ["mundillo", "soy nuevo"]


class Recolector:
    """
    Esta clase recolecta los distintos recursos que están disponibles,
    en un sólo objeto, con los siguientes atributos:
        data: diccionario con toda la información recolectada.
        message_list: lista de las palabras en el mensaje.
        message: el mensaje.
        ** Los siguientes atributos pueden ya están registrados en "data".
        installables: lista de instalables encontrados en el mensaje.
        installation: booleano, si hay indicios de requerir info de instalación.
        keywords: palabras clave detectadas, que se pueden asociar con recursos.
        beginner: booleano, si es posible que el usuario diga ser nuevo.
    """
    def __init__(self, message):
        self.message = message
        matches = re.finditer("\w+", self.message.lower())
        self.message_list = [self.message[match.start():match.end()] for match in matches]

        # Añade el atributo 'keywords'.
        self.get_keywords()

        # Añade los atributos esenciales, basándose en las variables globales (las bases de datos y las
        # listas de palabras clave).
        self.installables = [software for software in installables_list if software.lower() in self.message_list]
        self.installation = re.search("instal", self.message) is not None
        self.keywords = [keyword for keyword in self.all_keywords if keyword in self.message_list]
        self.beginner = any([True for kwd in beginner_keywords if re.search(kwd, message)])

        # Añade el atributo 'data'.
        self.recolect_data()

    def get_keywords(self):
        # Obtiene las palabras clave registradas en cada elemento de la base de datos de
        # los instalables y de recursos personalizados.
        custom_items = [custom_contents[item]["keywords"] for item in custom_contents]
        #custom_keywords = set([keyword.lower() for all_kws in custom_items for keyword in all_kws])
        custom_keywords = set([keyword for all_kws in custom_items for keyword in all_kws])

        installable_items = [item[each]["keywords"] for item in [installables[item]["custom"] for item in installables] for each in item]
        installable_keywords = set([keyword for keywords in installable_items for keyword in keywords])
        #installable_keywords = set([keyword for keywords in installable_items for keyword in keywords])
        #installable_keywords = set([keyword for keyword in installable_items])

        self.all_keywords = custom_keywords.union(installable_keywords)

    def get_info_installation(self, installable):
        # Obtiene el/los links con instrucciones de instalación
        # del instalable indicado.
        resources = installables[installable]
        custom = resources["custom"]
        if custom:
            for rsc in custom:
                if rsc:
                    keywords = custom[rsc]["keywords"]
                    if "instalación" in keywords or "instalacion in keywords":
                        return custom[rsc]["urls"]
        return []

    def get_installable_info(self, installable):
        # Obtiene todos los atributos del elemento en la base de datos
        # de los instalables.
        data = installables[installable].copy()
        del data["custom"]
        return data

    def get_info_installable_keywords(self, installable, keywords):
        # Reúne los recursos de elementos de "instalables".
        resources = installables[installable]
        custom = resources["custom"]
        data_found = []
        # Genera lista de los elementos que contienen las palabras clave
        # los guarda como diccionarios, "título" y "num" que es el número de
        # palabras clave que fueron detectadas en el recurso específico.
        for rsc in resources["custom"]:
            resource_keywords = resources["custom"][rsc]["keywords"]
            total = sum([True for key in keywords if key in resource_keywords])
            if total > 0:
                data_found.append({"title":rsc, "num": total})
        # Ordena los elementos por los que contienen más palabras clave y luego elimina los
        # elementos duplicados.
        ordered = sorted(data_found, key = lambda x:x["num"], reverse = False)
        all_titles = set([i["title"] for i in data_found])
        dic = dict([(item["title"], item["num"]) for item in ordered])
        relevance_filtering = sorted(dic, key = lambda x:dic[x], reverse = True)

        # Un diccionario del contenido encontrado, ordenado según el número de palabras
        # clave que coinciden.
        recolected = dict([(item, custom[item]) for item in relevance_filtering])
        return recolected

    def get_info_keywords(self, keywords):
        # Lo mismo que 'get_info_installable_keywords' pero de los recursos personalizados.
        resources = custom_contents
        data_found = []
        for rsc in resources:
            resource_keywords = resources[rsc]["keywords"]
            total = sum([True for key in keywords if key in resource_keywords])
            if total > 0:
                data_found.append({"title":rsc, "num": total})

        ordered = sorted(data_found, key = lambda x:x["num"], reverse = False)
        all_titles = set([i["title"] for i in data_found])
        dic = dict([(item["title"], item["num"]) for item in ordered])
        relevance_filtering = sorted(dic, key = lambda x:dic[x], reverse = True)

        recolected = dict([(item, resources[item]) for item in relevance_filtering])
        return recolected

    def get_info_beginner(self):
        # Debe obtener los recursos para principiantes
        # que deben añadirse pronto.
        return {}

    def recolect_data(self):
        # Recolecta los recursos disponibles, dependiendo de si hay o no
        # indicio de que se requieran.
        data = {
                "installables":{},
                "installation":{},
                "installable_keywords":{},
                "custom_from_keywords":{},
                "beginner":False
                }
        if self.installables:
            for installable in self.installables:
                data["installables"][installable] = self.get_installable_info(installable)

            if self.installation:
                data["installation"] = True

            if self.keywords:
                for installable in self.installables:
                    data["installable_keywords"][installable] = self.get_info_installable_keywords(installable, self.keywords)
                data["custom_from_keywords"] = self.get_info_keywords(self.keywords)

        else:
            if self.keywords:
                data["custom_from_keywords"] = self.get_info_keywords(self.keywords)

        if self.beginner:
            data["beginner"] = True

        self.data = data
