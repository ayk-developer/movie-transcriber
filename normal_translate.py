from googletrans import Translator

def translate_list(list_to_translate):
    translator = Translator()
    translations = translator.translate(list_to_translate,dest = 'en')
    return_list = []
    for translation in translations:
        return_list.append(translation.text)
    return return_list