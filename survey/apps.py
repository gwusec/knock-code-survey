from django.apps import AppConfig


from django.apps import AppConfig
import os 

from django.conf import settings
#from django.core.management import call_command

blacklist_from_file = []

def read_blacklist_from_file():
    with open(os.path.join(settings.PROJECT_ROOT,"../survey/blacklist/blacklist.txt")) as blacklist:
        for code in blacklist:
            code = code.rstrip("\r\n")
            blacklist_from_file.append(code)

class SurveyConfig(AppConfig):
    name = 'survey'

    def ready(self):
        read_blacklist_from_file()
