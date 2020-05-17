import requests
#BeautifulSoup es una biblioteca que me permite transformar documentos html o xml
#en un árbol de obbjetos  de tipos segun su tag.
from bs4 import BeautifulSoup

from datetime import datetime

def consultar_rss(tokens, url):
    #guardo el contenido
    try:
        resp = requests.get(url)

    except:
        print("ERROR EN PETICION")
        return []
    #proceso el xml y lo combierto en un árbol de tipos
    soup = BeautifulSoup(resp.content, features="xml")

    #guardo los objetos con la etiqueta item
    items = soup.findAll('item')

    news_items = []

#recorro los items extrayenndo la información que me interesa
    for item in items:
        news_item = {}
        news_item['title'] = item.title.text
        news_item['description'] = item.description.text
        news_item['link'] = item.link.text
        fecha = item.pubDate.text[:16]
        news_item['fecha'] = datetime.strptime(fecha,'%a, %d %b %Y').date()
       
   

        news_items.append(news_item)
    
    return news_items
def consultar_abc(tokens,url):
    return []