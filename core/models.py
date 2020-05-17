from django.db import models
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from googletrans import Translator
from unidecode import unidecode
from django.contrib.auth.models import User
from extraccion.scrappers import consultar_rss
from extraccion.apis import consultar_twitter
import re #Para regex

LENGTH = 255

class Consulta(models.Model):
    """
    Representa una consulta que efectúa el usuario en la base de datos
    Documentar esto en la Arquitectura que realmente no existe catalogador sino que 
    se trata dentro de Models.
    A través de la consulta se modela el catalagodor de opiniones.
    #ELIMINAMOS FECHAS?
    
    """
    peticion = models.CharField(max_length = LENGTH, db_index=True)
    fecha_inicial = models.DateField(blank= True, null=True)
    fecha_final = models.DateField(blank=True, null=True)
    user = models.ForeignKey(User,null = True, on_delete=models.SET_NULL)
    MATCHING_UMBRAL_DB = 0.8
    MATCHING_UMBRAL_OUT = 1

    def obtener_opiniones(self, update = False):
        """
        Obtiene las opiniones de las fuentes existentes y de consultas previas en la BD
        update: Declara si es necesario buscar en las fuentes existentes aunque existan opiniones distintas
        """
       
     
        tokens = self.devolver_tokens_procesados()
        opiniones = self.obtener_opiniones_desde_db(tokens)
           
        #Comprobar si no existe una consulta previa exactamente igual
        if (update):
            opiniones_fuera = self.obtener_opiniones_desde_fuera(tokens)
            opiniones.extend(opiniones_fuera)

        opiniones = [x for x in opiniones if self.en_fecha(x)] #Nos quedamos solo con las que están en fecha
        self.guardar_consultas(opiniones)
        

        return opiniones
        
        
    def guardar_consultas(self, opiniones):
        """
        Guarda las consultas en la BD junto con el resto de opiniones
        """
        repetida = Consulta.objects.filter(peticion = self.peticion)
        if repetida:
            repetida = repetida[0]
            opiniones_no_reps = [opinion for opinion in opiniones if opinion not in repetida.opiniones.all() ]
            for n in opiniones_no_reps:
                repetida.opiniones.add(n)
            repetida.save()
        else:
            self.save()
            for n in opiniones:
                self.opiniones.add(n)
            self.save()

    def obtener_opiniones_desde_fuera(self,tokens):
        """
        tokens: Lista de palabras relacionadas con la consulta
        Devuelve una lista de opiniones de las fuentes actuales en el sistema
        """
        fuentes = Fuente.objects.all()
       
        opiniones_sin_procesar = []
        for fuente in fuentes:
            opiniones_sin_procesar.extend(fuente.consultar_fuente(tokens))

        opiniones_finales = []
     
        for opinion in opiniones_sin_procesar:
            punt_titulo = self.calcular_puntuacion(tokens,opinion['title'])
            punt_cuerpo = self.calcular_puntuacion(tokens,opinion['description'])

            if punt_cuerpo + punt_titulo > Consulta.MATCHING_UMBRAL_OUT and not Opinion.objects.filter(url = opinion['link']):
                #Creamos las opiniones y las guardamos en la bd con create
                opiniones_finales.append(Opinion.objects.create(nombre=re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',opinion['title']),
                                                 fecha=opinion['fecha'],
                                                 url=opinion['link']))
        
      

        return opiniones_finales
    

        
    def obtener_opiniones_desde_db(self, tokens):
        """
        tokens: Lista de palabras relacionadas con la consulta
        Devuelve una lista de opiniones calculadsa desde peticiones previas hechas a la BD
      
        """
        opiniones = []
        resultados = []

        #Recorremos las consultas de la BD a ver si hay alguna parecida.
        #¿Por que sobre las consultas, por que de las opiniones solo tenemos su título
        #Es más significativo buscar consultas similares
        
        #Podríamos filtrar aquí también la fecha de la consulta y ahorrarnos el código siguiente
    
        for palabra in tokens:
            for sym in tokens[palabra]['sinonimos_raiz']:
                resultados.extend(Consulta.objects.filter(peticion__icontains = sym))
                #Mirar también en opiniones
            resultados.extend(Consulta.objects.filter(peticion__icontains = tokens[palabra]['orig']))
        
        resultados = list(set(resultados))

        for r in resultados:
            if self.calcular_puntuacion(tokens,r.peticion) >= Consulta.MATCHING_UMBRAL_DB: #Umbral por el que se considera que las consutlas son iguales
                #¿Por que no comparar con la fecha de las consultas?
                # Porque las fechas solo importan para descartar opiniones. 
                #Aunque esto se puede cambiawr para que vaya más rápido
                
                #ASOCIAMOS OPINIONES A NUESTRA CONSULTA
                opiniones.extend(r.opiniones.all())

        opiniones = list(set(opiniones))
    
        return opiniones

    def en_fecha(self,n):
        valido = True
        if self.fecha_final != None:
            if self.fecha_inicial != None:
                if ( n.fecha <= self.fecha_inicial or n.fecha >= self.fecha_final):
                    valido = False
            else:
                if (n.fecha >= self.fecha_final):
                    valido = False
        elif self.fecha_inicial != None:
             if n.fecha <= self.fecha_inicial:
                 valido = False

        return valido

    def calcular_puntuacion(self,tokens, texto):
        """
        POSIBLEMENTE SEA MÁS CORRECTO QUE SEA UN MÉTODO DE CLASE
        Calcula una puntuación de viabilidad al texto
        0 -> Si la noticia no tiene nada que ver con los tokens de la consulta
        > 1 . Si la noticia tiene varias palabras dentro

        Una mejroa próxima es utilizar una sigmoide.
        """

        puntuacion = 0
        texto = unidecode(texto.lower())
        for palabra in tokens:
            for sym in tokens[palabra]['sinonimos_raiz']:
                ocurrencias = texto.count(sym) #Contamos la ocurrencia de la palabra en el etexto
                puntuacion += 0.1*ocurrencias

            ocurrencias = texto.count(tokens[palabra]['orig'])
            puntuacion += 0.3*ocurrencias #Si se encuentra la palabra de forma literal se da 0.4
            
            ocurrencias = texto.count(tokens[palabra]['raiz'])
            puntuacion += 0.2*ocurrencias #Si se encuentra la raiz se da 0.2
    
        return puntuacion
    


    def devolver_tokens_procesados(self):
        """
        A partir de la petición almacenada en la consulta devuelve una estructura 
        en diccionario de la siguiente forma
        {
            token1: {
                sinonimos : [sinonimo1, sinonimo 2]
                sinonimos_raiz: [sinonimo_raiz1, sinonimo_raiz2],
                raiz: raiz_token_1,
                orig: token1

            }
            token2:{
                sinonimos : [sinonimo1, sinonimo 2]
                sinonimos_raiz: [sinonimo_raiz1, sinonimo_raiz2]
                raiz: raiz_token_2
            } 
        }
        Todos los sinonimos contienen solo la raiz aplicando el algoritmo de snowball stemmer.
        No se ha empleado lematización por que nltk no tiene soporte para el español.
        """

        trans = Translator()
        texto_procesado = unidecode(self.peticion.lower()) #Quitamos acentos y pasamos a minusculas
        tokens = word_tokenize(texto_procesado,'spanish')
        tokens_completos = {}
        #Utilizamos NLTK para primero eliminar las stopwords(la,el etc)
        #Posteriormente usamos wordnet para extraer sinónimos
        stemmer = SnowballStemmer('spanish')
        for token in tokens:
            if token not in stopwords.words('spanish'):
                sinonimos = []
                syms = []
                try:
                    #Traducimos a inglés 
                    syms = wordnet.synsets(trans.translate(token,src='es',dest='en').text)[0].lemma_names('spa')
                    for sym in syms: 
                        sinonimos.append(stemmer.stem(sym))
                except:
                    print("No se encontraron sinónimos para {}".format(token))
                    
                tokens_completos[token] = {
                    'sinonimos': syms,
                    'sinonimos_raiz': sinonimos,
                    'raiz': '',
                    'orig': token,
                }
        #Sacamos la raíz principal de la palabra de ltexto
        
        for token in tokens_completos:
            tokens_completos[token]['raiz'] = stemmer.stem(token)
    
        return tokens_completos

    def __str__(self):
        return self.peticion


class Fuente(models.Model):
    nombre = models.CharField(max_length=LENGTH)
    url = models.URLField()
    description = models.TextField()

    def consultar_fuente(self, tokens):
        """
        Llamada distintas funciones de extracción de datos
        dependiendo del nombre. Actúa coimo interfazx entre los extractores de fuente
        y el manejador de catálogo

        Recibe una lista de tokens por los que se buscará información
        
        Devuelve una lista de los siguientes objetos:

        { 
            'title': '', (string)
            'description': '', (string)
            'link': '' (string)
            'fecha': ''(date)
        }
        """

        if self.nombre == 'lavanguardia' :
            return consultar_rss(tokens, self.url)
        elif self.nombre == 'elpais':
            return consultar_rss(tokens, self.url)
        elif self.nombre == 'elideal':
            return consultar_rss(tokens,self.url)
        elif self.nombre == 'twitter':
            return consultar_twitter(tokens)
        else:
            raise NotImplementedError("La fuente {} no está implementada".format(self.nombre))
    def __str__(self):
        return self.nombre

class Opinion(models.Model):
    """
    Representa una opinion dada
    nombre: titulo de la opinion o descripcion
    fecha: fecha emitida
    url: Url dodne se puede encontrar más información
    consultas: consultas que están relacionadas con la noticia
    fuente: fuente de donde se ha extraido la noticia
    """
    nombre = models.CharField(max_length=LENGTH)
    fecha = models.DateField()
    url = models.URLField(db_index=True) #Lo vamos a usar intensivamente para evitar tener repetidos
    consultas = models.ManyToManyField(Consulta, related_name='opiniones', blank=True)
    fuente = models.ForeignKey(Fuente, null = True, on_delete = models.SET_NULL)

    def __str__(self):
        return self.nombre

class Tag(models.Model):
    nombre = models.CharField(max_length=LENGTH)
    opiniones = models.ManyToManyField(Opinion, related_name='tags')

