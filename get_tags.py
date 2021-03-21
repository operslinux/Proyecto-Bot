import re
import pickle
from utils import KaliTools

KaliTools = KaliTools()


with open("help_messages.pick", "rb") as file:
    data=file.read()
    file.close()
messages=pickle.loads(data)

all_tools = [ tool.lower() for tool in KaliTools.tools_list ]

tags_keywords = {
    "error":["error"],
    "installation":["instal"],
    "programming_language":["python", "c++", "java", "bash"],
    "new_to_this_world":[""],
    "keyword":["boot", "usb", "pdf", "curso", "máquina virtual", "payload", "audio", "red", "wifi"]
}

#<programming language>
#<new to this world>
#<keyword>
class GetTags:
    def __init__(self, message):
        matches = re.finditer("\w+", message.lower())
        self.message_list = [ message[match.start():match.end()] for match in matches ]
        self.message = ' '.join(x for x in self.message_list)
        #
        self.program_tags = self.program_tags()
        self.error_tags = self.error_tags()
        self.installation_tags = self.installation_tags()
        self.new_to_this_world_tags = self.new_to_this_world_tags()
    def error_tags(self):
        return "error" in self.message_list
    def program_tags(self):
        return [ tool for tool in all_tools if tool in self.message_list ]
    def installation_tags(self):
        if re.search("instal", self.message) is not None:
            return True
        return False
    def new_to_this_world_tags(self):
        if re.search("mundo", self.message) is not None:
            print(self.message)
            print("*"*12)
        if re.search("soy nuevo", self.message) is not None:
            print(self.message)
            print("*"*12)


for message in messages:
    tags = GetTags(message)
    tags.program_tags
    x=tags.program_tags

class Tags:
    def __init__(self):
        pass
    def add_tag(self):
        pass
    def tags(self):
        pass
    def get_tag_resources(self):
        pass






