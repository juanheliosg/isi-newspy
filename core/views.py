from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.forms import QueryForm
from core.models import Consulta
from datetime import datetime
# Create your views here.

class QueryProcessorView(LoginRequiredMixin, View):
    form_class = QueryForm
    template_name = 'index.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})
    
    def post(self, request,*args,**kwargs):
        
        form = self.form_class(request.POST)
        if form.is_valid():
            fecha_inicial = request.POST['fecha_inicial']
            #Formateamos las fechas
            if fecha_inicial != "":
                fecha_inicial = datetime.strptime(request.POST['fecha_inicial'],"%d/%m/%Y").date()
            else:
                fecha_inicial = None
            fecha_final = request.POST['fecha_final']
            if fecha_final != "":
                fecha_final = datetime.strptime(request.POST['fecha_final'],"%d/%m/%Y").date()
            else:
                fecha_final = None
            #Creamos la consulta con los datos pasados
            consulta = Consulta(
                peticion = request.POST['peticion'],
                fecha_inicial = fecha_inicial,
                fecha_final = fecha_final,
                user = request.user
            )
                 
            opiniones = consulta.obtener_opiniones(update=True)
            
            return render(request, self.template_name, {'form': form, 'opiniones': opiniones, 'peti':True, 'consulta': consulta})

        return render(request, self.template_name, {'form':form, 'peti':False})





