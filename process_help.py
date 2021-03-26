import re
import json

installables = json.loads(open("resources/installables.json","r").read())
installables_list = [item.lower() for item in installables]

custom_contents = json.loads(open("resources/custom_contents.json","r").read())

beginner_keywords = ["mundo", "mundillo", "soy nuevo"]

class Recolector:
    def __init__(self, message):
        self.message = message
        matches = re.finditer("\w+", self.message.lower())
        self.message_list = [self.message[match.start():match.end()] for match in matches]

        self.get_keywords()

        self.installables = [software for software in installables_list if software in self.message_list]
        self.installation = re.search("instal", self.message) is not None
        self.keywords = [keyword for keyword in self.all_keywords if keyword in self.message_list]
        self.beginner = any([True for kwd in beginner_keywords if re.search(kwd, message)])

        self.recolect_data()

    def get_keywords(self):
        custom_items = [custom_contents[item]["keywords"] for item in custom_contents]
        custom_keywords = set([keyword.lower() for all_kws in custom_items for keyword in all_kws])

        installable_items = [item[each]["keywords"] for item in [installables[item]["custom"] for item in installables] for each in item]
        installable_keywords = set([keyword.lower() for keywords in installable_items for keyword in keywords])

        self.all_keywords = custom_keywords.union(installable_keywords)

    def get_info_installation(self, installable):
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
        return installables[installable]

    def get_info_installable_keywords(self, installable, keywords):
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
        return {}

    def recolect_data(self):
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
