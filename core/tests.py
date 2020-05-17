from django.test import TestCase
from core.models import Consulta, Opinion
from datetime import date

# Create your tests here.
# Como correr los tests sin usar la db python manage.py shell < core/test.py


class ObtenerFromDB(TestCase):
    @classmethod
    def setUpTestData(cls):

        c1 = Consulta.objects.create(peticion="educación y coronavirus en españa")
        c2 = Consulta.objects.create(peticion="sistema educativo universitario")
        c3 = Consulta.objects.create(peticion="historia de la educación superior")
        c4 = Consulta.objects.create(peticion="Analisis de las enseñanzas medias en granada")
        c5 = Consulta.objects.create(peticion="Informes de los ministros de educación y universidad")

        o1 = Opinion.objects.create(nombre="Coronavirus en España. Consecuencias en la educación",
                                    fecha=date(2020,3,14),
                                    url="https://example.com/arplane/box.html")
        c1.opiniones.add(o1)

        o2 = Opinion.objects.create(nombre="La universidad 2014 en cifras",
                                    fecha=date(2014,3,14),
                                    url="https://example.com/airplan/box.html")
        c2.opiniones.add(o2)
        o3 = Opinion.objects.create(nombre="La enseñanza superior en el siglo XIX",
                                    fecha=date(1994,2,14),
                                    url="https://example.com/airpane/box.html")
        c3.opiniones.add(o3)
        o4 = Opinion.objects.create(nombre="Bonificación del 99 en universidades andaluzas",
                                    fecha=date(2018,3,14),
                                    url="https://example.com/airpne/bo.html")
        c2.opiniones.add(o4)
        o5 = Opinion.objects.create(nombre="Resolución ministerio de universidad",
                                    fecha=date(2020,3,14),
                                    url="https://example.com/aiane/box.html")
        c5.opiniones.add(o5)

        o6 = Opinion.objects.create(nombre="Resolución ministerio de educación",
                                    fecha=date(2020,3,23),
                                    url="https://example.com/aiane/abox.html")
        c5.opiniones.add(o6)

        c1.save()
        c2.save()
        c3.save()
        c4.save()
        c5.save()

    def test_obtenter_desde_db(self):
        c = Consulta(peticion="Educación universitaria en españa",
                    fecha_inicial= date(2010,1,1),
                    fecha_final=date(2020,5,1))
        noticias = c.obtener_noticias()
        #Funciona! 
        self.assertGreaterEqual(len(noticias),1)


def test_tokens_procesados(c):
    tokens = c.devolver_tokens_procesados()
    print(tokens)
    assert(len(tokens) > 0)
    

c = Consulta(peticion='Problemas de la educación en españa')

test_tokens_procesados(c)
