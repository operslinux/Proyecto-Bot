from utils import get_installable_post_id

class Installable:
    def __init__(self, name):# {{{
        self.name = name
        self.description = None
        self.homepage = None
        self.download_page = None
        self.docs = None
        self.post_id = None
    def get_description(self):
        # Cargar contenidos del diccionario.
        name = self.name
        description = self.description
        homepage = self.homepage
        download_page = self.download_page
        docs = self.docs
        # Reemplazar los símbolos para evitar problemas con el formato HTML.
        name = name.replace("<", "&lt;")

        a = f"Nombre:\n<code>{name}</code>\n\n"
        b = f"Descripción:\n<code>{description}</code>\n\n"
        c = f"Página principal:\n{homepage}\n\n"
        d = f"Página de descarga:\n{download_page}\n\n"
        e = f"Documentación:\n{docs}\n\n"
        # Unir contenidos encontrados
        formatted = a
        if description:
            formatted += b
        if homepage:
            formatted += c
        if download_page:
            formatted += d
        if docs:
            formatted += e
        return formatted
    def get_data_dict(self):
        return {
                "homepage": self.homepage,
                "description":self.description,
                "download":self.download_page,
                "docs":self.docs,
                "post_id":self.post_id,
                "custom":{}
                }
    def format_data(self):
        # Cargar contenidos del diccionario.
        name = self.name
        description = self.description
        homepage = self.homepage
        download_page = self.download_page
        docs = self.docs
        # Reemplazar los símbolos para evitar problemas con el formato HTML.
        name = name.replace("<", "&lt;")

        a = f"Nombre:\n<code>{name}</code>\n\n"
        b = f"Descripción:\n<code>{description}</code>\n\n"
        c = f"Página principal:\n{homepage}\n\n"
        d = f"Página de descarga:\n{download_page}\n\n"
        e = f"Documentación:\n{docs}\n\n"
        # Unir contenidos encontrados
        formatted = a
        if description:
            formatted += b
        if homepage:
            formatted += c
        if download_page:
            formatted += d
        if docs:
            formatted += e
        return formatted
    def set_description(self, text):
        self.description = text
    def set_download_page(self, url):
        self.download_page = url
    def set_docs(self, url):
        self.docs = url
    def set_homepage(self, url):
        self.homepage = url
# }}}

class CustomItem:
    def __init__(self, title):# {{{
        self.title = title
        self.description = None
        self.keywords = []
        self.urls = []
        self.files = []
        self.post_id = None
    def get_data_dict(self):
        return {
                "post_id":self.post_id,
                "description":self.description,
                "keywords":self.keywords,
                "urls":self.urls,
                "files":self.files
                }
    def get_description(self):
        # Cargar contenidos del diccionario.
        title = self.title
        description = self.description
        keywords = str(self.keywords)
        urls = self.urls
        files = self.files
        # Reemplazar los símbolos para evitar problemas con el formato HTML.
        title = title.replace("<", "&lt;")
        keywords = keywords.replace("<", "&lt;")

        urls = "".join([f"<code>{idx}:</code> {url}\n" for idx, url in enumerate(urls, 1)])

        b = f"Título:\n<code>{title}</code>\n\n"
        z = f"Descripción:\n<code>{description}</code>\n\n"
        d = f"Enlaces:\n{urls}\n"
        e = f"Archivos: <code>{len(files)} ↓ ↓ ↓ ↓</code>\n\n"
        # Unir contenidos encontrados
        formatted = b
        if description:
            formatted += z
        if urls:
            formatted += d
        if files:
            formatted += e
        return formatted
    def format_data(self):
        # Cargar contenidos del diccionario.
        title = self.title
        description = self.description
        keywords = str(self.keywords)
        urls = self.urls
        files = self.files
        # Reemplazar los símbolos para evitar problemas con el formato HTML.
        title = title.replace("<", "&lt;")
        keywords = keywords.replace("<", "&lt;")

        urls = "".join([f"<code>{idx}:</code> {url}\n" for idx, url in enumerate(urls, 1)])

        b = f"Título del contenido:\n<code>{title}</code>\n\n"
        z = f"Descripción:\n<code>{description}</code>\n\n"
        c = f"Palabras clave:\n<code>{str(keywords)}</code>\n\n"
        d = f"Enlaces:\n{urls}\n"
        e = f"Archivos: <code>{len(files)}</code>\n\n"
        # Unir contenidos encontrados
        formatted = b
        if description:
            formatted += z
        formatted += c
        if urls:
            formatted += d
        if files:
            formatted += e
        return formatted
    def add_file(self, file_id):
        self.files.append(file_id)
    def set_urls(self, text, entities):
        urled = [entity for entity in entities if entity["type"] == "url"]
        urls = [text[entity["offset"]:entity["offset"]+entity["length"]] for entity in urled]
        self.urls.extend(urls)
    def set_keywords(self, text):
        self.keywords = [x.strip(" ") for x in text.split(",")]
    def set_description(self, description):
        self.description = description
# }}}

class InstallableItem:
    def __init__(self, installable, channel_url):# {{{
        self.channel_url = channel_url
        self.installable = installable
        self.urls = []
        self.files = []
        self.description = None
        self.keywords = []
        self.title = None
        self.post_id = None
    def set_description(self, description):
        self.description = description
    def get_description(self):
        # Cargar contenidos del diccionario.
        installable = self.installable
        title = self.title
        description = self.description
        keywords = str(self.keywords)
        urls = self.urls
        files = self.files
        post_id = get_installable_post_id(installable)
        #try:
        #    post_id = get_installable_post_id(installable)
        #except:
        #    post_id = "0"
        # Reemplazar los símbolos para evitar problemas con el formato HTML.
        title = title.replace("<", "&lt;")
        installable = installable.replace("<", "&lt;")
        keywords = keywords.replace("<", "&lt;")

        urls = "".join([f"<code>{idx}:</code> {url}\n" for idx, url in enumerate(urls, 1)])

        #a = f"Contenido relacionado con:\n<code>{installable}</code>\n\n"
        a = f'Contenido relacionado con:\n<a href ="{self.channel_url}/{post_id}">{installable}</a>\n\n'
        ##<a href="http://www.example.com/">inline URL</a>
        b = f"Título:\n<code>{title}</code>\n\n"
        z = f"Descripción:\n<code>{description}</code>\n\n"
        d = f"Enlaces:\n{urls}\n"
        e = f"Archivos: <code>{len(files)}, ↓ ↓ ↓ ↓</code>\n\n"
        # Unir contenidos encontrados
        formatted = a + b + z
        if urls:
            formatted += d
        if files:
            formatted += e
        return formatted
    def get_data_dict(self):
        return {
                "installable":self.installable,
                "title":self.title,
                "description":self.description,
                "keywords":self.keywords,
                "urls":self.urls,
                "files":self.files,
                "post_id":self.post_id
                }
    def format_data(self):
        # Cargar contenidos del diccionario.
        installable = self.installable
        title = self.title
        description = self.description
        keywords = str(self.keywords)
        urls = self.urls
        files = self.files
        # Reemplazar los símbolos para evitar problemas con el formato HTML.
        title = title.replace("<", "&lt;")
        installable = installable.replace("<", "&lt;")
        keywords = keywords.replace("<", "&lt;")

        urls = "".join([f"<code>{idx}:</code> {url}\n" for idx, url in enumerate(urls, 1)])

        a = f"Instalable:\n<code>{installable}</code>\n\n"
        b = f"Título del contenido:\n<code>{title}</code>\n\n"
        z = f"Descripción:\n<code>{description}</code>\n\n"
        c = f"Palabras clave:\n<code>{str(keywords)}</code>\n\n"
        d = f"Enlaces:\n{urls}\n"
        e = f"Archivos: <code>{len(files)}</code>\n\n"
        # Unir contenidos encontrados
        formatted = a + b + z + c
        if urls:
            formatted += d
        if files:
            formatted += e
        return formatted

    def add_file(self, file_id):
        self.files.append(file_id)

    def set_urls(self, text, entities):
        urled = [entity for entity in entities if entity["type"] == "url"]
        urls = [text[entity["offset"]:entity["offset"]+entity["length"]] for entity in urled]
        self.urls.extend(urls)

    def set_keywords(self, text):
        self.keywords = [x.strip(" ") for x in text.split(",")]

    def set_title(self, title):
        self.title = title# }}}
