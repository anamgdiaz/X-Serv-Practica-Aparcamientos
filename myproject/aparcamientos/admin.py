from django.contrib import admin

# Register your models here.

from .models import Aparcamiento,Usuario,Comentario,Seleccionados


admin.site.register(Aparcamiento)
admin.site.register(Usuario)
admin.site.register(Comentario)
admin.site.register(Seleccionados)
