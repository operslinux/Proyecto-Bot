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
installables_list = [item.lower() for item in installables]

# Cargar la base de datos de recursos personalizados (cualquier tipo de recurso).
custom_contents = json.loads(open("resources/custom_contents.json","r").read())

# Palabras clave donde alguien dice ser iniciante.
beginner_keywords = [, "mundillo", "soy nuevo"]


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
        self.installables = [software for software in installables_list if software in self.message_list]
        self.installation = re.search("instal", self.message) is not None
        self.keywords = [keyword for keyword in self.all_keywords if keyword in self.message_list]
        self.beginner = any([True for kwd in beginner_keywords if re.search(kwd, message)])

        # Añade el atributo 'data'.
        self.recolect_data()

    def get_keywords(self):
        # Obtiene las palabras clave registradas en cada elemento de la base de datos de
        # los instalables y de recursos personalizados.
        custom_items = [custom_contents[item]["keywords"] for item in custom_contents]
        custom_keywords = set([keyword.lower() for all_kws in custom_items for keyword in all_kws])

        installable_items = [item[each]["keywords"] for item in [installables[item]["custom"] for item in installables] for each in item]
        installable_keywords = set([keyword.lower() for keywords in installable_items for keyword in keywords])

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
                    if "instal" in keywords:
                        return custom[rsc]["urls"]
        return []

    def get_installable_info(self, installable):
        # Obtiene todos los atributos del elemento en la base de datos
        # de los instalables.
        return installables[installable]

    def get_info_installable_keywords(self, installable, keywords):
        # Reúne todos los recursos (del instalable) que incluyen las palabras clave.
        # Debe revisarse para que no haya recursos repetidos
        # y que estén ordenados dependiendo de cuántas palabras clave coincidan         ########## REVISAR #########.
        resources = installables[installable]
        custom = resources["custom"]
        data_found = []
        if custom:
            for keyword in keywords:
                for rsc in custom:
                    if rsc:
                        keywords = custom[rsc]["keywords"]
                        if keyword in keywords:
                            data_found.append({rsc:custom[rsc]})
        return data_found

    def get_info_keywords(self, keywords):
        # Lo mismo que 'get_info_installable_keywords' pero de los recursos personalizados.
        # Debe revisarse para que no haya recursos repetidos
        # y que estén ordenados dependiendo de cuántas palabras clave coincidan         ########## REVISAR #########.
        resources = custom_contents
        data_found = []
        for keyword in keywords:
            if resources:
                for rsc in resources:
                    if rsc:
                        keywords = resources[rsc]["keywords"]
                        if keyword in keywords:
                            data_found.append({rsc:resources[rsc]})
        return data_found

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
                "beginner":{}
                }
        if self.installables:
            for installable in self.installables:
                data["installables"][installable] = self.get_installable_info(installable)

            if self.installation:
                for installable in self.installables:
                    data["installation"][installable] = self.get_info_installation(installable)

            if self.keywords:
                for installable in self.installables:
                    data["installable_keywords"][installable] = self.get_info_installable_keywords(installable, self.keywords)
                data["custom_from_keywords"] = self.get_info_keywords(self.keywords)

        else:
            if self.keywords:
                data["custom_from_keywords"] = self.get_info_keywords(self.keywords)

            if self.beginner:
                data["beginner"] = {"data": self.get_info_beginner()}

        self.data = data
