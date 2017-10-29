#!/usr/bin/env python3
#coding=utf8

# Этот скрипт используется для перевода на русский язык
#
# Аргументы командной строки: нету
# Входные данные: из буфера обмена: xsel -o
#
# Зависимости: 
# - python3
# - jinja2
# - sudo apt-get install xsel
# - для того, что бы уведомление от notify-send не висело 10 секунд
#   надо его "пропатчить" установив пакет: http://leolik.blogspot.ru/2012/06/notify-osd.html


import os,requests,functools,argparse

class BaseTranslate(object):
  def get_requests_kwargs(self, need_translate):
    return {
      'url':self.url,
      'params':[('key',self.KEY),('text',need_translate),('lang',self.LANG)],
    }


  def prepare_need_translate(self,need_translate):
    return functools.reduce(self.concat_wordbreak, map(lambda x:x.strip(), need_translate.split('\n')))

  def get_need_translate(self):
    return os.popen('xsel').read()

  # Time of message showing based on human reading speed
  def get_notify_send_time(self, translate):
  	read_speed = 1800. / 60 # signs per second
  	time = len(translate) / read_speed 
  	time = int(time) * 1000 # conver to miilis
  	
  	if time < 1000:
  		time = 1000
  	return time

  def send_message(self, need_translate, translate=''):
    os.system(u'notify-send -t {time} -u critical "{need_translate}" "{translate}"'.format(
      need_translate=need_translate,
      translate=translate,
      time=self.get_notify_send_time(translate),
    ))

  def concat_wordbreak(self, x, y):
    if len(x)==0:
        return y
    #different kind of unicoda dashes http://www.fileformat.info/info/unicode/category/Pd/list.htm
    if x[-1] in ('-',u'\u058a',u'\u05be',u'\u2010',u'\u2011',u'\u2012',u'\u2013',u'\u2014',u'\u2015',u'\uff63',u'\uff0d'):
        return x[:-1]+y
    else:
        return x+' '+y

  def translate(self):
    need_translate = self.prepare_need_translate(self.get_need_translate())
    translated = requests.get(**self.get_requests_kwargs(need_translate)).json()
    code = translated.get('code',200)
    if code==200:
      self.send_message(need_translate=need_translate, translate=self.make_message(translated))
    else:
      self.send_message('ERROR', 'code={code} message={message}'.format(code=code,message=translated.get('message')))



class YandexTranslate(BaseTranslate):
  KEY='trnsl.1.1.20150408T074646Z.aeb6eb702fe117f4.a49cf4d308b1d9fd0710d8e3ec7043a373f49538'
  url='https://translate.yandex.net/api/v1.5/tr.json/translate'
  LANG='en-ru'
  notify_send_time=1000

  def make_message(self,translate):
    return u' '.join(translate['text'])

class YandexSlovari(BaseTranslate):
  KEY='dict.1.1.20170817T033442Z.5db93772620bdf37.cd3bd3a91df0c3ab56b3ac89d6315452f12639fd'
  url='https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
  LANG='en-ru'
  template_name = os.path.join(os.path.dirname(os.path.realpath(__file__)),'ya-slovari.jinja')
  notify_send_time=3000

  def make_message(self,translate):
    import jinja2
    with open(self.template_name) as f:
      tmpl = jinja2.Template(f.read())
    return tmpl.render({'translate':translate}).strip()

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--trtype",default="translate",choices=['translate','slovari'])
  args = parser.parse_args()
  if args.trtype=='translate':
    YandexTranslate().translate()
  else:
    YandexSlovari().translate()

