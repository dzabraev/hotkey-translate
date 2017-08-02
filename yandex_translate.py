#!/usr/bin/env python3
#coding=utf8

# Этот скрипт используется для перевода на русский язык
#
# Аргументы командной строки: нету
# Входные данные: из буфера обмена: xsel -o
#
# Зависимости: 
# - python3
# - sudo apt-get install xsel
# - для того, что бы уведомление от notify-send не висело 10 секунд
#   надо его "пропатчить" установив пакет: http://leolik.blogspot.ru/2012/06/notify-osd.html


import os,requests

KEY='trnsl.1.1.20150408T074646Z.aeb6eb702fe117f4.a49cf4d308b1d9fd0710d8e3ec7043a373f49538'
LANG='ru'

def send_message(need_translate, translate):
    os.system(u'notify-send -t 1000 -u critical "{need_translate}" "{translate}"'.format(
        need_translate=need_translate,
        translate=translate))

def translate():
    need_translate = os.popen('xsel').read()
    translated = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate',params=[('key',KEY),('text',need_translate),('lang',LANG)]).json()
    code = translated['code']
    if code==200:
        send_message(need_translate=need_translate, translate=u' '.join(translated['text']))
    else:
        send_message('ERROR code={code}'.format(code=code))


if __name__=="__main__":
    translate()

