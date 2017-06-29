"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from aparcamientos import views
from django.views.static import *
from myproject import settings

urlpatterns = [
    url(r'^change.css/', 'aparcamientos.views.personalizar'),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_URL}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'aparcamientos.views.pagina_principal'),
    url(r'^login' , 'aparcamientos.views.loginuser'),
    url(r'^logout', 'aparcamientos.views.mylogout'),
    url(r'^aparcamientos/$', 'aparcamientos.views.aparcamientos'),
    url(r'^aparcamientos/(.*)', 'aparcamientos.views.aparcamientos_id'),
    url(r'^about/', 'aparcamientos.views.about'),
    url(r'^(.*)/xml/', 'aparcamientos.views.usuarios_xml'),
    url(r'^(.*)/$', 'aparcamientos.views.usuarios'),
]

"""
from django.conf.urls import include, url
from django.contrib import admin
#from aparcamientos import views
import aparcamientos.views as aparca_views
#from myproject import settings
import myproject.settings as my_sets
from django.views.static import *

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),  #localhost:1234/admin
    url(r'^$', aparca_views.pag_pal, name='Pagina principal de la app'),    #localhost:1234/
    url(r'^login', aparca_views.userlogin, name='Pagina de loguearse'),    #localhost:1234/login
    url(r'^logout', aparca_views.userlogout, name='Pagina de desloguearse'),    #localhost:1234/logout
    url(r'^aparcamientos/$', aparca_views.aparcamientos, name='Pagina con todos los aparcamientos'),  #localhost:1234/aparcamientos
    url(r'^aparcamientos/(.*)', aparca_views.aparcamientos_id, name='Pagina de un aparcamiento'),   #localhost:1234/aparcamiento/id
    url(r'^about/', aparca_views.about, name='Pagina con la info'),     #localhost:1234/about
    url(r'^(.*)/xml', aparca_views.users_xml, name='Pagina xml con los usuarios'),  #localhost:1234/id/xml
    url(r'^(.*)/$', aparca_views.users, name='Pagina del usuario id'),    #localhost:1234/id
    url(r'^main.css/', aparca_views.personaliza, name='Pagina para personalizar el css'),   #localhost:1234/main.css
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_URL}),
]
"""
