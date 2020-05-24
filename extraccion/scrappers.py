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
        if item != None and item.title != None:
            news_item['title'] = item.title.text
            if item.description:
                news_item['description'] = item.description.text
            else:
                news_item['description'] = ''
            if item.link:
                news_item['link'] = item.link.text
            else:
                news_item['link'] = ''
            if item.pubDate:
                fecha = item.pubDate.text[:16]
                news_item['fecha'] = datetime.strptime(fecha,'%a, %d %b %Y').date()
            else:
                news_item['fecha'] = ''
 
        if news_item:
            news_items.append(news_item)
            
    print("PERIÓDICO CONSULTADO")
    
    return news_items
def consultar_abc(tokens,url):
    return []