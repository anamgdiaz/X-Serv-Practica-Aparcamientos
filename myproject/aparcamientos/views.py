from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.template import Context
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import xml.etree.ElementTree as etree
from xml.dom.minidom import Document, parse
import xml.dom.minidom as dom

import datetime
import sys
from .parser import get_data
from django.http import QueryDict
import urllib


# Create your views here.
@csrf_exempt
def login_form(request):

    formulario = '<form action="login" method="POST">'
    formulario += 'Nombre<br><input type="text" name="Usuario"><br>'
    formulario += 'Contraseña<br><input type="password" name="Password"><br>'
    formulario += '<br><input type="submit" value="Entrar"></form>'
    return formulario

@csrf_exempt
def loginuser(request):

	username = request.POST['Usuario']
	password = request.POST['Password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request,user)
		direcc = '/' + str(user)
		return redirect(direcc)
	else:
		Error = "Por favor, introduzca un usuario y contraseña válidos"
		template = get_template("fail.html")
		c = Context ({'Error': Error})
		renderizado = template.render(c)
		return HttpResponse(renderizado)

def lista_megustas():

    lista_todos = Aparcamiento.objects.all()
    lista_ordenada = lista_todos.order_by("-contador_megusta")[:5]
    Response = "LISTADO DE APARCAMIENTOS CON MÁS ME GUSTA<br><br>"
    Existe = False
    for i in lista_ordenada:
        megustas = i.contador_megusta
        #comentarios = Comentario.objects.filter(aparcamiento=i)
        if megustas != 0:
            Response += "<li><a href=" + i.content_url + ">" + i.nombre + "<br></a>"
            Response += "Dirección: " + i.clase_vial + " " + i.localizacion + ", nº " + str(i.num)
            Response += "<br><a href=http://localhost:1234/aparcamientos/" + i.entidad + ">" + "Más información<br></a><br>"
            Existe = True
    if Existe == False:
        Response += "Aún no se han registrado comentarios para ningún aparcamiento"

    Response += "</br></br>"
    return Response

def paginas_personales():

	Lista = "PÁGINAS DE USUARIOS<br><br>"
	usuarios = User.objects.all()
	for i in usuarios:
		try:
			pagina = Usuario.objects.get(nombre=i.id).titulo_pagina
		except ObjectDoesNotExist:
			pagina = "Página de " + i.username
		Lista += "<a href=http://localhost:1234/" + i.username + ">" + pagina + "</a>	Usuario: " + i.username + "<br>"

	return Lista

def lista_aparcamientos():

	lista = ''
	aparcamientos = Aparcamiento.objects.all()
	for aparcamiento in aparcamientos:
		nombre_aparcamiento = aparcamiento.nombre
		url_aparcamiento = aparcamiento.entidad
		lista += '<li><p>' + nombre_aparcamiento + '<a href="' + url_aparcamiento + '">	--> Más información</a></p></li>'

	return lista

def aparcamientos_seleccionados(user,request):

	user_object = User.objects.get(username=user)

	try:
		usuario = Usuario.objects.get(nombre=user_object)
		lista_seleccionados = Seleccionados.objects.filter(selector=usuario)

		paginator = Paginator(lista_seleccionados,5)
		page = request.GET.get('page')
		try:
			seleccionados = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			seleccionados = paginator.page(1)
		except EmptyPage:
		     # If page is out of range (e.g. 9999), deliver last page of results.
			seleccionados = paginator.page(paginator.num_pages)

		lista = "Listado de aparcamientos seleccionados por " + user + "<br>"

		for i in seleccionados:
			lista += "<br><li>Fecha de selección: " + str(i.fecha_seleccion)
			lista += "<br><a href=" + i.aparcamiento.content_url + ">" + i.aparcamiento.nombre + "<br></a>"
			lista += "Dirección: " + i.aparcamiento.clase_vial + " " + i.aparcamiento.localizacion + ", nº " + str(i.aparcamiento.num)
			lista += "<br><a href=http://localhost:1234/aparcamientos/" + i.aparcamiento.entidad + ">" + "Más información</a><br>"
	except ObjectDoesNotExist:
		lista = "El usuario aún no ha seleccionado ningún aparcamiento"
		seleccionados = ""


	return lista,seleccionados

def accesibles(value):
	accesibles = '<form action="" method="POST">'
	accesibles += '<button type="submit" name="Accesible" value="' + str(value) + '"> Accesibles</button></form>'

	return accesibles

@csrf_exempt
def pagina_principal(request):

	formulario = login_form(request)
	list_megustas = lista_megustas()
	users = paginas_personales()

	value = 1
	accesible = accesibles(value)

	template = get_template("index.html")

	if request.user.is_authenticated():
		username = str(request.user)
		formulario = 'Bienvenido ' + username
		formulario += '<br><br><a href="http://localhost:1234/logout" > Logout </a>'

	if request.method == 'POST':

		key = request.body.decode("utf-8").split('=')[0]

		if key == 'Accesible':
			value = request.POST['Accesible']

			if value == '1':
				lista_accesibles = Aparcamiento.objects.filter(accesibilidad=1)
				lista = '<a href="http://localhost:1234/" > Volver </a>'
				value = 0
				for i in lista_accesibles:
					nombre_aparcamiento = i.nombre
					url_aparcamiento = i.content_url
					lista += "<li><p>" + nombre_aparcamiento + "</p><a href=" + url_aparcamiento + ">" + url_aparcamiento + "</a></li>"
			else:
				lista = '<a href="http://localhost:1234/" > Volver </a>'
				aparcamientos = Aparcamiento.objects.all()
				for aparcamiento in aparcamientos:
					nombre_aparcamiento = aparcamiento.nombre
					url_aparcamiento = aparcamiento.entidad
					lista += '<li><p>' + nombre_aparcamiento + '. URL del aparcamiento: ' + '<a href="aparcamientos/' + url_aparcamiento + '">	⇾ Más información</a></br></p>'
				value = 1

			accesible = accesibles(value)
			c = Context({'login': formulario, 'list_users':lista, 'accesible': accesible})

	else:

		init = Aparcamiento.objects.all()

		if len(init) == 0:
			get_data()


		c = Context({'login': formulario, 'list':list_megustas, 'list_users':users, 'accesible': accesible})

	renderizado = template.render(c)
	return HttpResponse(renderizado)

def mylogout(request):
	logout(request)
	return redirect("/")

@csrf_exempt
def usuarios(request, peticion):

	formulario = '<form action="" method="POST">'
	formulario += '<br>Introduzca un título nuevo a su página personal<br><input type="text" name="Titulo">'
	formulario += '<input type="submit" value=" Actualizar"></form>'

	css = '<form action="" method="POST">'
	css += 'Modifique el tamaño de letra<br><input type="text" name="Letra">'
	css += '<br><br>Modifique el color de letra	<input type="color" name="Color"><br>'
	css += '<br><input type="submit" value="Modificar"></form>'


	aparcamientos = Aparcamiento.objects.all()

	lista= "<br>LISTADO DE APARCAMIENTOS<br><br>"
	for aparcamiento in aparcamientos:
		nombre_aparcamiento = aparcamiento.nombre
		lista += nombre_aparcamiento
		lista += '<form action="" method="POST">'
		lista += '<button type="submit" name="Seleccionar" value="' + nombre_aparcamiento + '">Seleccionar</button><br></form>'

	user_object= User.objects.get(username=peticion)

	if request.method == 'POST':
		key = request.body.decode("utf-8").split('=')[0]
		if key == "Titulo":
			titulo = request.POST['Titulo']
			try:
				user = Usuario.objects.get(nombre=user_object)
				user.titulo_pagina = titulo
				user.save()
			except ObjectDoesNotExist:
				p = Usuario(nombre=user_object, titulo_pagina=titulo)
				p.save()

		elif key == "Seleccionar":
			nombre_aparcamiento = request.POST['Seleccionar']
			today = datetime.datetime.today()


			try:
				selector = Usuario.objects.get(nombre=user_object)
				aparcamiento = Aparcamiento.objects.get(nombre=nombre_aparcamiento)
			except:
				p = Usuario(nombre=user_object)
				p.save()
				selector = Usuario.objects.get(nombre=user_object)


			Check = False
			lista_usuario = Seleccionados.objects.filter(selector=selector)
			for i in lista_usuario:
				if	nombre_aparcamiento == i.aparcamiento.nombre:
					Check=True

			if Check == False:
				p = Seleccionados(aparcamiento=aparcamiento, selector=selector, fecha_seleccion=today)
				p.save()

		elif key == "Letra":
			letra = request.POST['Letra']
			color = request.POST['Color']

			try:
				user = Usuario.objects.get(nombre=user_object)
			except:
				p = Usuario(nombre=user_object)
				p.save()
				user = Usuario.objects.get(nombre=user_object)
			if letra == "":
				letra = "15"

			user.letra = letra
			user.color = color
			user.save()

	lista_seleccionados, seleccionados= aparcamientos_seleccionados(peticion,request)


	if request.user.is_authenticated():
		username = str(request.user)
		if peticion != username:  #Si no es igual es que solo puedo acceder a la parte publica, ya qu eno es la mia
			template = get_template("publicuser.html")
			titulo_pagina = "Página pública de " + peticion + "<br><br>"
			form_user = 'Bienvenido ' + username
			form_user += '<br><br><a href="http://localhost:1234/logout" > Logout </a>'
			c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'titulo': titulo_pagina, 'login':form_user})
		else:	    #Si es igual es que es la mia y puedo acceder a la parte privada, ya que es lamia
			template = get_template("privateuser.html")
			try:
				titulo_pagina = Usuario.objects.get(nombre=user_object).titulo_pagina
			except ObjectDoesNotExist:
				titulo_pagina = "Página personal de " + str(request.user) + "<br><br>"
			c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'lista': lista, 'form': formulario, 'css':css, 'titulo': titulo_pagina})
	else:
		template = get_template("publicuser.html")
		titulo_pagina = "Página pública de " + peticion + "<br><br>"
		form_user = 'Para loguearse vaya al botón de Inicio'
		c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'titulo': titulo_pagina, 'login':form_user})


	renderizado = template.render(c)
	return HttpResponse(renderizado)

def personalizar(request):
	if request.user.is_authenticated():
		user_object = User.objects.get(username=request.user)
		user = Usuario.objects.get(nombre=user_object)
		letra = user.letra
		color = user.color
	else:
		letra = "14px"
		color = "#FCFCFC"

	css = get_template("change.css")
	c = Context({'letra':letra, 'color':color})
	renderizado = css.render(c)

	return HttpResponse(renderizado, content_type="text/css")

def usuarios_xml(request, peticion):

	user_object = User.objects.get(username=peticion)

	doc = Document()
	cont = doc.createElement("Contenidos")
	doc.appendChild(cont)
	info = doc.createElement("infoDataset")
	cont.appendChild(info)
	nombre = doc.createElement("Nombre")
	info.appendChild(nombre)
	ptext = doc.createTextNode("XML de aparcamientos seleccionados por el usuario " + peticion)
	nombre.appendChild(ptext)
	url = doc.createElement("url")
	info.appendChild(url)
	ptext = doc.createTextNode("http://localhost:1234/" + peticion + "/xml/")
	url.appendChild(ptext)
	aparc = doc.createElement("Aparcamientos")
	cont.appendChild(aparc)

	try:
		usuario = Usuario.objects.get(nombre=user_object)
		lista_seleccionados = Seleccionados.objects.filter(selector=usuario)


		for i in lista_seleccionados:
			item = doc.createElement("Contenido")
			aparc.appendChild(item)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "ID-ENTIDAD")
			ptext = doc.createTextNode(i.aparcamiento.entidad)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "NOMBRE")
			ptext = doc.createTextNode(i.aparcamiento.nombre)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "DESCRIPCION")
			ptext = doc.createTextNode(i.aparcamiento.descripcion)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "ACCESIBILIDAD")
			if i.aparcamiento.accesibilidad == True:
				acces = 1
			else:
				acces = 0
			ptext = doc.createTextNode(str(acces))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "CONTENT_URL")
			ptext = doc.createTextNode(i.aparcamiento.content_url)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "LOCALIZACION")
			ptext = doc.createTextNode(i.aparcamiento.localizacion)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "CLASE VIAL")
			ptext = doc.createTextNode(i.aparcamiento.clase_vial)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "TIPO NUM")
			ptext = doc.createTextNode(i.aparcamiento.tipo_num)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "NUM")
			ptext = doc.createTextNode(str(i.aparcamiento.num))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "LOCALIDAD")
			ptext = doc.createTextNode(i.aparcamiento.localidad)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "PROVINCIA")
			ptext = doc.createTextNode(i.aparcamiento.provincia)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "CODIGO POSTAL")
			ptext = doc.createTextNode(str(i.aparcamiento.codigo_postal))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "BARRIO")
			ptext = doc.createTextNode(i.aparcamiento.barrio)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "DISTRITO")
			ptext = doc.createTextNode(i.aparcamiento.distrito)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "COORDENADA X")
			ptext = doc.createTextNode(str(i.aparcamiento.coordenada_x))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			atributo.setAttribute("nombre", "COORDENADA Y")
			ptext = doc.createTextNode(str(i.aparcamiento.coordenada_y))
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			item.appendChild(atributo)
			datos = doc.createElement("DATOSDECONTACTO")
			item.appendChild(datos)
			atributo = doc.createElement("atributo")
			datos.appendChild(atributo)
			atributo.setAttribute("nombre", "TELEFONO")
			ptext = doc.createTextNode(i.aparcamiento.telefono)
			atributo.appendChild(ptext)
			atributo = doc.createElement("atributo")
			datos.appendChild(atributo)
			atributo.setAttribute("nombre", "EMAIL")
			ptext = doc.createTextNode(i.aparcamiento.email)
			atributo.appendChild(ptext)
	except:
		print("")


	xml = doc.toprettyxml(indent=" ")
	return HttpResponse(xml, content_type = "text/xml")

@csrf_exempt
def aparcamientos(request):

	lista = lista_aparcamientos()

	filtrar = '<form action="" method="POST">'
	filtrar += '<br><br><input type="text" name="distrito">'
	filtrar += '<input type="submit" value="Filtrar por distrito">'

	template = get_template("aparcamientos.html")

	if request.user.is_authenticated():
		username = str(request.user)
		form_user = 'Bienvenido ' + username
		form_user += '<br><br><a href="http://localhost:1234/logout" > Logout </a>'
	else:
		form_user = "Para loguearse vaya al botón de Inicio"

	if request.method == "POST":
		filtro_distrito = request.POST['distrito']
		filtro_distrito = filtro_distrito.upper()

		if filtro_distrito == '':
			lista_filtrada = "No ha introducido ningún filtro, introduzca distrito para filtrar " + lista
		else:
			aparcamientos_filtrados = Aparcamiento.objects.all()
			Encontrado = False
			lista_filtrada = "Los aparcamientos en el " + filtro_distrito + " son: "
			for i in aparcamientos_filtrados:
				if filtro_distrito == i.distrito:
					Encontrado = True
					nombre_aparcamiento = i.nombre
					url_aparcamiento = i.content_url
					lista_filtrada += "<p>" + nombre_aparcamiento + "</p><li><a href=" + url_aparcamiento + ">" + url_aparcamiento + "</a></li>"


			if Encontrado == False:		#No es un distrito válido el que se ha introducido y no ha entrado por el bucle anterior
				lista_filtrada = "Introduzca un nuevo distrito. " + filtro_distrito + " no es válido"


		c = Context({'distrito': filtrar, 'lista': lista_filtrada, 'login':form_user})

	else:

		c = Context({'distrito': filtrar, 'lista': lista, 'login':form_user})


	renderizado = template.render(c)
	return HttpResponse(renderizado)

@csrf_exempt
def aparcamientos_id(request, recurso):

    template = get_template("aparcamientos.html")
    num_megustas = 0

    if request.method == 'POST':
        key = request.body.decode("utf-8").split('=')[0]
        print(key)

        #tipo = request.POST
        #print(tipo)
        #qd = urllib.unquote(tipo).decode("utf-8")
        #qd = QueryDict(tipo).decode("utf-8")
        #qd.getlist('Me Gusta')
        #print(qd)
        if key == 'Me+Gusta':
            aparcamiento = Aparcamiento.objects.get(entidad=recurso)
            aparcamiento.contador_megusta = aparcamiento.contador_megusta + 1
            aparcamiento.save()
            num_megustas = aparcamiento.contador_megusta
        else:
            coment = request.POST['Comentario']
            aparcamiento = Aparcamiento.objects.get(entidad=recurso)
            aparcamiento.contador_coments = aparcamiento.contador_coments + 1
            aparcamiento.save()

            p = Comentario (aparcamiento= aparcamiento, coment=coment)
            p.save()



    try:
        aparcamiento = Aparcamiento.objects.get(entidad=recurso)

        nombre = aparcamiento.nombre
        descripcion = aparcamiento.descripcion
        accesibilidad = aparcamiento.accesibilidad
        localizacion = aparcamiento.localizacion
        via = aparcamiento.clase_vial
        num = aparcamiento.num
        localidad = aparcamiento.localidad
        provincia = aparcamiento.provincia
        codigo_postal = aparcamiento.codigo_postal
        barrio = aparcamiento.barrio
        distrito = aparcamiento.distrito
        coordenada_x = aparcamiento.coordenada_x
        coordenada_y = aparcamiento.coordenada_y
        telefono = aparcamiento.telefono
        email = aparcamiento.email

        if telefono == '':
            telefono = "No disponible"

        if email == '':
            email = "No disponible"

        if accesibilidad == 1:
            acces = "Libre"
        else:
            acces = "Ocupado"

        lista_aparcamientos = Aparcamiento.objects.all()
        list_coments = ""
        aparcamiento = Aparcamiento.objects.get(entidad=recurso)
        num_megustas = aparcamiento.contador_megusta
        for i in lista_aparcamientos:
            if i.entidad == recurso:
                comentarios = Comentario.objects.filter(aparcamiento=i)
                if len(comentarios) != 0:
                    list_coments = "<li><p>COMENTARIOS</p><ol>"
                    for j in comentarios:
                        list_coments += "<li>" + j.coment + "<br>"

                Response = "<p>INFORMACIÓN ACERCA DEL APARCAMIENTO CON ID: " + recurso + "</br></p>"
                Response += "<a href=" + i.content_url + ">" + i.nombre + "</a><br>"
                Response += "Descripción: " + descripcion + "</br>"
                Response += "Accesibilidad: " + acces + "</br>"
                Response += "Localización: " + via + " " + localizacion + ", nº " + str(num)
                Response += " " + localidad + " (" + str(codigo_postal) + ")</br>"
                Response += "Ubicación: " + barrio + " " + distrito + " Coordenadas: " + str(coordenada_x) + " , " + str(coordenada_y) + "<br><br>"
                Response += "INFORMACIÓN DE CONTACTO </br>"
                Response += "Teléfono: " + telefono + "</br>"
                Response += "Email: " + email + "</br>" + list_coments + "</ol>"
                if num_megustas != 0:
                    Response += "</br><li>Numero de me gustas es: " + str(num_megustas) + "<br>"
                else:
                    Response += "</br><li>Se el primero en indicar que te gusta la página<br>"

        if request.user.is_authenticated():
            username = str(request.user)
            form_user = 'Bienvenido ' + username
            form_user += '<br><br><a href="http://localhost:1234/logout" > Logout </a>'

            formulario = '<form action="" method="POST">'
            formulario += '<br>Puede introducir un comentario si lo desea ' + str(request.user) + '<br><input type="text" name="Comentario">'
            formulario += '<input type="submit" value="Comentar"></form>'
            Response += formulario

        else:
            form_user = "Para loguearse vaya al botón de Inicio"

        megusta = ''
        megusta += '<br> Indica que te gusta este aparcamiento</br>'
        megusta += '<form action="" method="POST">'
        megusta += '<button type="submit" name="Me Gusta" value="Me Gusta"> +1 </button></form>'
        Response += megusta

    except ObjectDoesNotExist:
        Response = "Este id no se corresponde con ningún aparcamiento"

    c = Context({'lista': Response, 'login': form_user})
    renderizado = template.render(c)
    return HttpResponse(renderizado)

def about(request):

    template = get_template("about.html")

    Cuerpo = "DESCRIPCIÓN DE LA APLICACIÓN DE APARCAMIENTOS DE MADRID<br><br>"
    Cuerpo += "------------------------------------ Página principal ---------------------------------------------------"
    Cuerpo += "<li> Tiene un menú bajo el banner en el que nos permite dirigirnos a Inicio (página principal), a Todos (listado de todos los aparcamientos) o a About (página de ayuda y explicación de la web) </li>"
    Cuerpo += "<li> Un botón Accesibles, que si se selecciona una vez mostrará un listado con sólo aquellos aparcamientos que estén disponibles en ese momento. Si se selecciona de nuevo, mostrará un listado con todos los aparcamientos registrados en la aplicación. Para volver a la página principal se selecciona 'Volver'.</li>"
    Cuerpo += "<li> Bajo el botón Accesibles hay un listado de páginas personales de usuario: Muestra un listado con la interfaz pública de los usuarios registrados en la aplicación. Se puede acceder a ellas seleccionando el enlace del título de sus páginas de usuario.</li>"
    Cuerpo += "<li> Listado de Aparcamientos con más me gusta: Mostrará los 5 aparcamientos más valorados por usuarios.</li></br></br>"
    Cuerpo += "------------------------------------ Página con los aparcamientos ---------------------------------------------------"
    Cuerpo += "<li> Se puede acceder a través del botón 'Todos' de la Página Principal.</li>"
    Cuerpo += "<li> Muestra un listado con todos los aparcamientos registrados junto con un enlace a 'Más Información' para cada aparcamiento. Este enlace mostrará información más detallada acerca de este aparcamiento y también sus comentarios.</li>"
    Cuerpo += "<li> Filtrar por distrito: permite el filtrado por un distrito seleccionado. Mostrará un listado de aquellos aparcamientos que se correspondan con el distrito introducido.</li></br></br>"
    Cuerpo += "------------------------------------ Interfaz pública de usuario ---------------------------------------------------"
    Cuerpo += "<li> Muestra un listado con los aparcamientos seleccionados por el usuario elegido. Sólo se visualizan de 5 en 5.</li>"
    Cuerpo += "<li> Tiene un menú bajo el banner en el que nos permite dirigirnos a Inicio (página principal), a Todos (listado de todos los aparcamientos) o a About (página de ayuda y explicación de la web) </li></br></br>"
    Cuerpo += "------------------------------------ Interfaz privada de usuario ---------------------------------------------------"
    Cuerpo += "<li> Un usuario podrá loguearse únicamente desde la Página Principal. Para ello debe rellenar el formulario superior. Una vez logueado, accede a su página personal de usuario. Donde puede encontrar: </li>"
    Cuerpo += "<li> El listado con los aparcamientos seleccionados por ese usuario, con un enlace a la página del aparcamiento y a su información. Si se accede a 'Más Información', se mostrará la página de ese aparcamiento junto con un formulario para que el usuario pueda poner comentarios si lo desea. </li>"
    Cuerpo += "<li> Formulario para cambiar el título de su página personal.</li>"
    Cuerpo += "<li> Formulario para cambiar el color y tamaño de letra de todas las páginas de la aplicación.</li>"
    Cuerpo += "<li> Listado con todos los aparcamientos registrados para poder seleccionarlos pulsando 'Seleccionar'.</li></br></br>"
    Cuerpo += "------------------------------------ Pie de pagina ---------------------------------------------------"
    Cuerpo += "<li> Si se selecciona el enlace Datos munimadrid, se redirecciona a la página original de la aplicación de Aparcamientos de Madrid.</li>"
    Cuerpo += "<li> Si se selecciona el enlace correspodiente al fichero XML muestra el XML con la información de todos los aparcamientos registrados en la página.</li></br></br>"
    Cuerpo += "------------------------------------ Página XML de un usuario ---------------------------------------------------"
    Cuerpo += "<li> Si se realiza el recurso 'usuario'/XML, se muestra el XML con la información de los aparcamientos seleccionados por el usuario introducido.</li></br></br>"

    c = Context({'lista': Cuerpo})
    renderizado = template.render(c)

    return HttpResponse(renderizado)
