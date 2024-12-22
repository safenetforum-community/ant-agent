#todo

local translation using gettext

xgettext -o locales/messages.pot {file.py}

--

msginit -l de -i locales/messages.pot -o locales/de/LC_MESSAGES/messages.po
msginit -l fr -i locales/messages.pot -o locales/fr/LC_MESSAGES/messages.po
msginit -l es -i locales/messages.pot -o locales/es/LC_MESSAGES/messages.po
msginit -l cn -i locales/messages.pot -o locales/cn/LC_MESSAGES/messages.po
msginit -l ru -i locales/messages.pot -o locales/ru/LC_MESSAGES/messages.po
msginit -l gb -i locales/messages.pot -o locales/gb/LC_MESSAGES/messages.po
msginit -l br -i locales/messages.pot -o locales/br/LC_MESSAGES/messages.po
msginit -l mx -i locales/messages.pot -o locales/mx/LC_MESSAGES/messages.po
msginit -l it -i locales/messages.pot -o locales/it/LC_MESSAGES/messages.po
msginit -l jp -i locales/messages.pot -o locales/jp/LC_MESSAGES/messages.po

msgfmt locales/de/LC_MESSAGES/messages.po -o locales/de/LC_MESSAGES/messages.mo
msgfmt locales/fr/LC_MESSAGES/messages.po -o locales/fr/LC_MESSAGES/messages.mo
etc...

import gettext 
import os 

# Set up message catalog access 
current_dir = os.path.dirname(__file__) 
locales_dir = os.path.join(current_dir, 'locales') 

def set_language(lang_code): 
    lang = gettext.translation('messages', localedir=locales_dir, languages=[lang_code])
    lang.install() 
    _ = lang.gettext 
    return _ 
    
# Mark strings for translation 
_ = set_language('de') 

# Switch to German (for example) 
print(_('Hello, world!'))
