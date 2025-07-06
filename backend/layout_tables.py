# layout_tables.py

# Таблицы соответствий для популярных языков
EN_RU_LAYOUT = dict(zip(
    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./`~@#$^&QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?Ёё',
    'йцукенгшщзхъфывапролджэячсмитьбю.ёЁ"№;:?ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,.'
))
RU_EN_LAYOUT = {v: k for k, v in EN_RU_LAYOUT.items()}

EN_UK_LAYOUT = dict(zip(
    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./`~@#$^&QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?ҐґЇїІіЄє',
    'йцукенгшщзхїфівапролджєячсмитьбю.ґҐ"№;:?ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,.'
))
UK_EN_LAYOUT = {v: k for k, v in EN_UK_LAYOUT.items()}

EN_DE_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMäöüßÄÖÜẞ',
    'qwertzuiopasdfghjkyxcvbnmQWERTZUIOPASDFGHJKYXCVBNMäöüßÄÖÜẞ'
))
DE_EN_LAYOUT = {v: k for k, v in EN_DE_LAYOUT.items()}

EN_FR_LAYOUT = dict(zip(
    'azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBNéèàçœùêâîôûëïüÿÉÈÀÇŒÙÊÂÎÔÛËÏÜŸ',
    'qwertyuiopasdfghjklzxcvbnQWERTYUIOPASDFGHJKLZXCVBNeeeeacoeueaaioueiuyEEACOEUEAAIOUEIUY'
))
FR_EN_LAYOUT = {v: k for k, v in EN_FR_LAYOUT.items()}

EN_ES_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMñÑáéíóúüÁÉÍÓÚÜ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMnNaeiouuAEIOUU'
))
ES_EN_LAYOUT = {v: k for k, v in EN_ES_LAYOUT.items()}

EN_IT_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMàèéìòùÀÈÉÌÒÙ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMàèéìòùÀÈÉÌÒÙ'
))
IT_EN_LAYOUT = {v: k for k, v in EN_IT_LAYOUT.items()}

EN_PL_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMąćęłńóśźżĄĆĘŁŃÓŚŹŻ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMacelnoszzACELNOSZZ'
))
PL_EN_LAYOUT = {v: k for k, v in EN_PL_LAYOUT.items()}

EN_TR_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMğüşöçİĞÜŞÖÇı',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMgusocIGUSOCi'
))
TR_EN_LAYOUT = {v: k for k, v in EN_TR_LAYOUT.items()}

EN_PT_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMáàâãçéêíóôõúÁÀÂÃÇÉÊÍÓÔÕÚ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMaaaaceeiioouAAAACEEIIOOU'
))
PT_EN_LAYOUT = {v: k for k, v in EN_PT_LAYOUT.items()}

EN_CS_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMáčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMacdeeinorstuuyzACDEEINORSTUUYZ'
))
CS_EN_LAYOUT = {v: k for k, v in EN_CS_LAYOUT.items()}

EN_HU_LAYOUT = dict(zip(
    'qwertzuiopőúasdfghjkléáűíyxcvbnmQWERTZUIOPŐÚASDFGHJKLÉÁŰÍYXCVBNMöüóÖÜÓ',
    'qwertyuiopouasdfghjkleaiyxcvbnmQWERTYUIOPOUASDFGHJKLEAIYXCVBNMouoOUO'
))
HU_EN_LAYOUT = {v: k for k, v in EN_HU_LAYOUT.items()}

EN_EL_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMάέήίΰαβγδεζηθικλμνξοπρσςτυφχψωΆΈΉΊΰΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMaehiabgdezhthiklmnxoprssstufchpoAEHIABGDEZHTHIKLMNXOPRSSTUFCHPO'
))
EL_EN_LAYOUT = {v: k for k, v in EN_EL_LAYOUT.items()}

EN_FI_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMäöåÄÖÅ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMaoaAOA'
))
FI_EN_LAYOUT = {v: k for k, v in EN_FI_LAYOUT.items()}

EN_SV_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMåäöÅÄÖ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMaoaAOA'
))
SV_EN_LAYOUT = {v: k for k, v in EN_SV_LAYOUT.items()}

EN_DA_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMæøåÆØÅ',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMaeoAEO'
))
DA_EN_LAYOUT = {v: k for k, v in EN_DA_LAYOUT.items()}

EN_NL_LAYOUT = dict(zip(
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM',
    'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
))
NL_EN_LAYOUT = {v: k for k, v in EN_NL_LAYOUT.items()}

LAYOUTS = {
    ('en', 'ru'): EN_RU_LAYOUT,
    ('ru', 'en'): RU_EN_LAYOUT,
    ('en', 'uk'): EN_UK_LAYOUT,
    ('uk', 'en'): UK_EN_LAYOUT,
    ('en', 'de'): EN_DE_LAYOUT,
    ('de', 'en'): DE_EN_LAYOUT,
    ('en', 'fr'): EN_FR_LAYOUT,
    ('fr', 'en'): FR_EN_LAYOUT,
    ('en', 'es'): EN_ES_LAYOUT,
    ('es', 'en'): ES_EN_LAYOUT,
    ('en', 'it'): EN_IT_LAYOUT,
    ('it', 'en'): IT_EN_LAYOUT,
    ('en', 'pl'): EN_PL_LAYOUT,
    ('pl', 'en'): PL_EN_LAYOUT,
    ('en', 'tr'): EN_TR_LAYOUT,
    ('tr', 'en'): TR_EN_LAYOUT,
    ('en', 'pt'): EN_PT_LAYOUT,
    ('pt', 'en'): PT_EN_LAYOUT,
    ('en', 'cs'): EN_CS_LAYOUT,
    ('cs', 'en'): CS_EN_LAYOUT,
    ('en', 'hu'): EN_HU_LAYOUT,
    ('hu', 'en'): HU_EN_LAYOUT,
    ('en', 'el'): EN_EL_LAYOUT,
    ('el', 'en'): EL_EN_LAYOUT,
    ('en', 'fi'): EN_FI_LAYOUT,
    ('fi', 'en'): FI_EN_LAYOUT,
    ('en', 'sv'): EN_SV_LAYOUT,
    ('sv', 'en'): SV_EN_LAYOUT,
    ('en', 'da'): EN_DA_LAYOUT,
    ('da', 'en'): DA_EN_LAYOUT,
    ('en', 'nl'): EN_NL_LAYOUT,
    ('nl', 'en'): NL_EN_LAYOUT,
}

LANG_CHARSETS = {
    'en': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    'ru': set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'),
    'uk': set('абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'),
    'de': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZäöüßÄÖÜẞ'),
    'fr': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZéèêëàâæçîïôœùûüÿÉÈÊËÀÂÆÇÎÏÔŒÙÛÜŸ'),
    'es': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúüñÁÉÍÓÚÜÑ'),
    'it': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZàèéìòùÀÈÉÌÒÙ'),
    'pl': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZąćęłńóśźżĄĆĘŁŃÓŚŹŻ'),
    'tr': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZğüşöçİĞÜŞÖÇı'),
    'pt': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáàâãçéêíóôõúÁÀÂÃÇÉÊÍÓÔÕÚ'),
    'cs': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ'),
    'hu': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóöőúüűÁÉÍÓÖŐÚÜŰ'),
    'el': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZάέήίΰαβγδεζηθικλμνξοπρσςτυφχψωΆΈΉΊΰΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'),
    'fi': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZäöåÄÖÅ'),
    'sv': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZåäöÅÄÖ'),
    'da': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZæøåÆØÅ'),
    'nl': set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'),
}

def detect_charset(text: str):
    counts = {lang: sum(c in charset for c in text) for lang, charset in LANG_CHARSETS.items()}
    # Возвращаем язык с максимальным количеством совпадений
    return max(counts, key=counts.get)

def fix_keyboard_layout(text: str, from_lang: str, to_lang: str) -> str:
    layout = LAYOUTS.get((from_lang, to_lang))
    if layout:
        return ''.join(layout.get(c, c) for c in text)
    return text 