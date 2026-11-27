"""Bloqueo temporal de intentos fallidos de inicio de sesión para ejecución local.
Para despliegues distribuidos configurar caché compartida (Redis, etc.).
"""
import hashlib
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponse

class LoginProtegido(LoginView):
    template_name='registration/login.html'
    intentos_maximos=5
    bloqueo_segundos=15*60
    def key(self):
        usuario=self.request.POST.get('username','').strip().lower()[:150]
        ip=self.request.META.get('REMOTE_ADDR','')
        digest=hashlib.sha256((usuario+'|'+ip).encode()).hexdigest()
        return 'login_intentos_'+digest
    def dispatch(self,request,*args,**kwargs):
        if request.method=='POST' and cache.get(self.key(),0)>=self.intentos_maximos:
            return HttpResponse('Acceso bloqueado temporalmente después de intentos fallidos.',status=429)
        return super().dispatch(request,*args,**kwargs)
    def form_invalid(self,form):
        key=self.key()
        value=cache.get(key,0)
        cache.set(key,value+1,self.bloqueo_segundos)
        return super().form_invalid(form)
    def form_valid(self,form):
        cache.delete(self.key())
        return super().form_valid(form)
