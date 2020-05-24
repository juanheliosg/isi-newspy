import tweepy #para conectarse a la API
import os #para conectarse al sistema operativo


#SOLO PARA TESTS
from dotenv import load_dotenv

#auth = tweepy.OAuthHandler()
def consultar_twitter(tokens):
    """
    Consulta las opiniones de twitter utilizando la API de twitter
    con el cliente tweepy. Se usan claves obtenidas de una APP
    de twitter que hemos creado para ello.

    La api de Twitter solo permite búsquedas en los últimos 7 días. Esto es
    algo a tener en cuenta a las consultas que se quieran hacer.

    Devuelve lo mismo que consultar fuentes siguiendo su especificación
    
    Tenemos limite de 150 request por hora
    """
   
    auth = tweepy.OAuthHandler(os.getenv('TWITTER_CONSUMER_TOKEN'),
                                os.getenv('TWITTER_CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN'), 
                           os.getenv('TWITTER_ACCESS_SECRET'))
    
    
    consulta_comb = ''
    
    for t in tokens:
        consulta_comb += tokens[t]['orig'] + ' OR '
    consulta_comb = consulta_comb[:len(consulta_comb)-4]

    search_res = []
    try:
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        for t in tokens:
            search_res.extend(api.search(q=tokens[t]['raiz'],result_type='popular',count=5,lang='es'))
        search_res.extend(api.search(q=consulta_comb,result_type='popular',count=5,lang='es'))
    except:
         print("ERROR CONECTANDOSE A LA API DE TWITTER")
         return []

    opiniones = []
    for tweet in search_res:
        if tweet and tweet.entities['urls']:
             #Elimnamos URLS por que son feas
            opiniones.append({
                'title': tweet.text,
                'description':'',
                'link': tweet.entities['urls'][0]['url'],
                'fecha': tweet.created_at.date() #Convertimos a formato date
              })
    
    print("TWITTER CONSULTADO")
    
    return opiniones
    


