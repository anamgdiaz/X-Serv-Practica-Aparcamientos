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


# Create your views here.
@csrf_exempt
def login_form(request):

    formulario = '<form action="login" method="POST">'
    formulario += 'Username<br><input type="text" name="Usuario"><br>'
    formulario += 'Password<br><input type="password" name="Password"><br>'
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
		Error = "Por favor, introduzca un usuario o contraseña válidos"
		template = get_template("error.html")
		c = Context ({'Error': Error})
		renderizado = template.render(c)
		return HttpResponse(renderizado)

def pie_pagina():

	url = 'http://datos.munimadrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?'
	url += 'vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=202584-0-aparcamientos-'
	url += 'residentes&mgmtid=e84276ac109d3410VgnVCM2000000c205a0aRCRD&preview=full'

	url2 = 'http://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?'
	url2 += 'vgnextoid=e84276ac109d3410VgnVCM2000000c205a0aRCRD&vgnextchannel='
	url2 += '374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default'

	#Así no queda feo en la plantilla
	url_pag = 'http://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?'
	url_pag += 'vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=202584-0-aparcamientos/'

	foot = '<html><body><p>Esta aplicación utiliza datos del portal de datos abiertos de la ciudad de Madrid. © Copyright'\
				+ '</p></body></html>'
	foot += '<a href=' + url2 + '>' + url_pag + '</a><br></br>'
	foot += '<a href=' + url + '>Descripción de los datos en formato XML</a>'

	return foot


def lista_comentarios():

	lista_todos = Aparcamiento.objects.all()
	lista_ordenada = lista_todos.order_by("-contador_coments")[:5]
	Response = "LISTADO DE APARCAMIENTOS MÁS COMENTADOS<br><br>"
	Existe = False
	for i in lista_ordenada:
		comentarios = Comentario.objects.filter(aparcamiento=i)
		if len(comentarios) != 0:
			Response += "<li><a href=" + i.content_url + ">" + i.nombre + "<br></a>"
			Response += "Dirección: " + i.clase_vial + " " + i.localizacion + ", nº " + str(i.num)
			Response += "<br><a href=http://localhost:1234/aparcamientos/" + i.entidad + ">" + "Más información<br></a>"
			Existe = True
	if Existe == False:
		Response += "Aún no se han registrado comentarios para ningún aparcamiento"

	Response += "<br><br>"
	return Response

def paginas_personales():

	Lista = "PÁGINAS PERSONALES DE USUARIO<br><br>"
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
		lista += '<li><p>' + nombre_aparcamiento + '<a href="' + url_aparcamiento + '">	⇾ Más información</a></p></li>'

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
	foot = pie_pagina()
	list_coments = lista_comentarios()
	users = paginas_personales()

	value = 1
	accesible = accesibles(value)

	template = get_template("index.html")

	if request.user.is_authenticated():				#He recibido un login de un usuario
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
					lista += '<p>' + nombre_aparcamiento + '<br>URL del aparcamiento: ' + '<a href="aparcamientos/' + url_aparcamiento + '">	⇾ Más información</a></br></p>'
				value = 1

			accesible = accesibles(value)
			c = Context({'login': formulario, 'footer': foot, 'list_users':lista, 'accesible': accesible})

	else:

		init = Aparcamiento.objects.all()

		if len(init) == 0:
			get_data() #PARSER


		c = Context({'login': formulario, 'footer': foot, 'list':list_coments, 'list_users':users, 'accesible': accesible})

	renderizado = template.render(c)
	return HttpResponse(renderizado)



def mylogout(request):
	logout(request)
	return redirect("/")


@csrf_exempt
def usuarios(request, peticion):

	foot = pie_pagina()

	formulario = '<form action="" method="POST">'
	formulario += '<br>Introduzca un título nuevo a su página personal<br><input type="text" name="Titulo">'
	formulario += '<input type="submit" value=" Actualizar"></form>'

	css = '<form action="" method="POST">'
	css += 'Modifique el tamaño de letra<br><input type="text" name="Letra">'
	css += '<br>Modifique el color de letra	<input type="color" name="Color"><br>'
	css += '<br><input type="submit" value="Modificar"></form>'


	aparcamientos = Aparcamiento.objects.all()

	lista= "<br>LISTADO DE APARCAMIENTOS<br><br>"
	for aparcamiento in aparcamientos:
		nombre_aparcamiento = aparcamiento.nombre
		lista += nombre_aparcamiento
		lista += '  <form action="" method="POST">'
		lista += '<button type="submit" name="Seleccionar" value="' + nombre_aparcamiento + '">Seleccionar</button><br></form>'

	user_object= User.objects.get(username=peticion)

	if request.method == 'POST':
		key = request.body.decode("utf-8").split('=')[0]
		if key == "Titulo":
			titulo = request.POST['Titulo']
			try:
				user = Usuario.objects.get(nombre=user_object)	#Si funciona es que ya existe
				user.titulo_pagina = titulo
				user.save()
			except ObjectDoesNotExist:
				p = Usuario(nombre=user_object, titulo_pagina=titulo)
				p.save()

		elif key == "Seleccionar":
			nombre_aparcamiento = request.POST['Seleccionar']
			today = datetime.datetime.today()

			#Búsqueda de ForeignKeys
			try:
				selector = Usuario.objects.get(nombre=user_object)		#Si funciona es que ya existe
				aparcamiento = Aparcamiento.objects.get(nombre=nombre_aparcamiento)
			except:
				p = Usuario(nombre=user_object)			#Si no existe, lo creo
				p.save()
				selector = Usuario.objects.get(nombre=user_object)		#Ahora ya sí existe

			#Compruebo si ese aparcamiento ya se ha seleccionado
			Check = False
			lista_usuario = Seleccionados.objects.filter(selector=selector)
			for i in lista_usuario:
				if	nombre_aparcamiento == i.aparcamiento.nombre:
					Check=True

			if Check == False:
				#Almaceno el aparcamiento seleccionado en su página personal
				p = Seleccionados(aparcamiento=aparcamiento, selector=selector, fecha_seleccion=today)
				p.save()

		elif key == "Letra":
			letra = request.POST['Letra']
			color = request.POST['Color']

			try:
				user = Usuario.objects.get(nombre=user_object)		#Si funciona es que ya existe
			except:
				p = Usuario(nombre=user_object)			#Si no existe, lo creo
				p.save()
				user = Usuario.objects.get(nombre=user_object)		#Ahora ya sí existe
			if letra == "":
				letra = "11"

			user.letra = letra
			user.color = color
			user.save()

	lista_seleccionados, seleccionados= aparcamientos_seleccionados(peticion,request)


	if request.user.is_authenticated():
		username = str(request.user)
		if peticion != username:
			template = get_template("public.html")
			titulo_pagina = "Página pública de " + peticion + "<br><br>"
			form_user = 'Bienvenido ' + username
			form_user += '<br><br><a href="http://localhost:1234/logout" > Logout </a>'
			c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'titulo': titulo_pagina, 'login':form_user, 'footer':foot})
		else:	#Estoy en mi página personal
			template = get_template("user.html")
			try:
				titulo_pagina = Usuario.objects.get(nombre=user_object).titulo_pagina
			except ObjectDoesNotExist:
				titulo_pagina = "Página personal de " + str(request.user) + "<br><br>"
			c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'lista': lista, 'form': formulario, 'css':css, 'titulo': titulo_pagina, 'footer':foot})
	else:
		template = get_template("public.html")
		titulo_pagina = "Página pública de " + peticion + "<br><br>"
		form_user = 'Para loguearse vaya al botón de Inicio'
		c = Context({'lista_selecc':lista_seleccionados, 'seleccionados':seleccionados, 'titulo': titulo_pagina, 'login':form_user, 'footer':foot})


	renderizado = template.render(c)
	return HttpResponse(renderizado)

def personalizar(request):
	if request.user.is_authenticated():
		user_object = User.objects.get(username=request.user)
		user = Usuario.objects.get(nombre=user_object)
		letra = user.letra
		color = user.color
	else:
		letra = "11px"
		color = "#8e7282"

	css = get_template("main.css")
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
	foot = pie_pagina()

	filtrar = '<form action="" method="POST">'
	filtrar += '<br><br><input type="text" name="distrito"><br>'
	filtrar += '<br><input type="submit" value="Filtrar por distrito">'

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
			lista_filtrada = "No ha introducido ningún filtro. Por favor introduzca un distrito para filtrar " + lista
		else:
			aparcamientos_filtrados = Aparcamiento.objects.all()
			Encontrado = False
			lista_filtrada = "Los aparcamientos filtrados en " + filtro_distrito + " son: "
			for i in aparcamientos_filtrados:
				if filtro_distrito == i.distrito:
					Encontrado = True
					nombre_aparcamiento = i.nombre
					url_aparcamiento = i.content_url
					lista_filtrada += "<p>" + nombre_aparcamiento + "</p><li><a href=" + url_aparcamiento + ">" + url_aparcamiento + "</a></li>"


			if Encontrado == False:		#No es un distrito válido el que se ha introducido y no ha entrado por el bucle anterior
				lista_filtrada = "Por favor introduzca un nuevo distrito. " + filtro_distrito + " no es un distrito válido"


		c = Context({'distrito': filtrar, 'lista': lista_filtrada, 'footer': foot, 'login':form_user})

	else:

		c = Context({'distrito': filtrar, 'lista': lista, 'footer': foot, 'login':form_user})


	renderizado = template.render(c)
	return HttpResponse(renderizado)

@csrf_exempt
def aparcamientos_id(request, recurso):

	foot = pie_pagina()
	template = get_template("aparcamientos.html")

	if request.method == 'POST':
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
		for i in lista_aparcamientos:
			if i.entidad == recurso:
				comentarios = Comentario.objects.filter(aparcamiento=i)
				if len(comentarios) != 0:		#Quiere decir que ese Aparcamiento no tiene comentarios, así que no muestro su lista
					list_coments = "<p>COMENTARIOS</p>"
					for j in comentarios:
						list_coments += j.coment + "<br>"
				Response = "<p>INFORMACIÓN ACERCA DEL APARCAMIENTO " + recurso + "</br></p>"
				Response += "<a href=" + i.content_url + ">" + i.nombre + "</a><br>"
				Response += list_coments + "<br>"
				Response += "Descripción: " + descripcion + "</br>"
				Response += "Accesibilidad: " + acces + "</br>"
				Response	+= "Localización: " + via + " " + localizacion + ", nº " + str(num)
				Response	+= " " + localidad + " (" + str(codigo_postal) + ")</br>"
				Response	+= "Ubicación: " + barrio + " " + distrito + " Coordenadas: " + str(coordenada_x) + " , " + str(coordenada_y) + "<br><br>"
				Response += "INFORMACIÓN DE CONTACTO </br>"
				Response += "Teléfono: " + telefono + "</br>"
				Response += "Email: " + email + "</br>"

		if request.user.is_authenticated():
			username = str(request.user)
			form_user = 'Bienvenido ' + username
			form_user += '<br><br><a href="http://localhost:1234/logout" > Logout </a>'

			formulario = '<form action="" method="POST">'
			formulario += '<br><br>Puede introducir un comentario si lo desea ' + str(request.user) + '<br><input type="text" name="Comentario"><br>'
			formulario += '<br><input type="submit" value="Enviar"></form>'
			Response += formulario #Sólo si está logueado

		else:
			form_user = "Para loguearse vaya al botón de Inicio"

	except ObjectDoesNotExist:
		Response = "Este id no se corresponde con ningún aparcamiento"

	c = Context({'lista': Response, 'footer': foot, 'login': form_user})
	renderizado = template.render(c)
	return HttpResponse(renderizado)


def about(request):

	foot = pie_pagina()
	template = get_template("ayuda.html")

	Response = "DESCRIPCIÓN DE LA APLICACIÓN DE APARCAMIENTOS DE MADRID<br><br>"
	Response += "<li> Página principal </li>"
	Response += "<p> Botón Todos: Muestra un listado con todos los aparcamientos registrados en la aplicación </p>"
	Response += "<p> Botón Ayuda: Muestra un texto de ayuda que describe el funcionamiento de la página </p>"
	Response += "<p> Botón Accesibles: Si se selecciona una vez mostrará un listado con sólo aquellos aparcamientos que estén disponibles."
	Response += " Si se selecciona de nuevo, mostrará un listado con todos los aparcamientos registrados en la aplicación."
	Response += " Para salir del menú Accesibles se seleccionará 'Volver'.</p>"
	Response += "<p>Listado de Aparcamientos más comentados: Mostrará los 5 aparcamientos más comentados por usuarios.</p>"
	Response += "<p>Listado de páginas personales de usuario: Mostrará un listado con la interfaz públicas de los usuarios registrados en"
	Response += " la aplicación. Se podrá acceder a ellas seleccionando el enlace del título de sus páginas de usuario.</p>"
	Response += "<li> Interfaz pública de usuario </li>"
	Response += "<p> Se mostrará un listado con los aparcamientos seleccionados por ese usuario. Sólo se verán de 5 en 5, pudiendo "
	Response += " seleccionar el enlace 'Next page' o 'Previous page' para visualizar los siguientes o anteriores.</p>"
	Response += "<p> Botón Inicio: Muestra de nuevo la página principal. </p>"
	Response += "<li> Página de aparcamientos </li>"
	Response += "<p> Se podrá acceder a través del botón 'Todos' de la Página Principal.</p>"
	Response += "<p> Muestra un listado con todos los aparcamientos registrados junto con un enlace a 'Más Información'. Este enlace "
	Response += "mostrará información más detallada acerca de este aparcamiento, incluídos sus comentarios.</p>"
	Response += "<p> Filtrar por distrito: permite el filtrado por un distrito seleccionado. Este distrito debe ser incluído sin tildes."
	Response += " Mostrará un listado de aquellos aparcamientos que se correspondan con el distrito introducido.</p>"
	Response += "<li> Interfaz privada </li>"
	Response += "<p> Un usuario podrá loguearse únicamente desde la Página Principal. Para ello debe rellenar el formulario superior."
	Response += " Una vez logueado, accede a su página personal de usuario. Donde podrá encontrar: </p>"
	Response += "<p> El listado con los aparcamientos seleccionados por ese usuario, con un enlace a la página del aparcamiento y a su"
	Response += " información. Si se accede a 'Más Información', se mostrará la página de ese aparcamiento junto con un formulario"
	Response += " para que el usuario pueda poner comentarios si lo desea. </p>"
	Response += "<p> Formulario para cambiar el título de su página personal.</p>"
	Response += "<p> Formulario para cambiar el color y tamaño de letra de todas las páginas de la aplicación.</p>"
	Response += "<p> Listado con todos los aparcamientos registrados para poder seleccionarlos pulsando 'Seleccionar'.</p>"
	Response += "<li> Pie de página </li>"
	Response += "<p> Enlace de la aplicación: Muestra la página original de la aplicación de Aparcamientos de Madrid.</p>"
	Response += "<p> Descripción de los datos: Muestra un XML con la información de todos los aparcamientos registrados en la página.</p>"
	Response += "<li> XML de usuario </li>"
	Response += "<p> Finalmente, si se realiza el recurso 'usuario'/XML, se mostrará un XML con la información de los aparcamientos"
	Response += " seleccionados por el usuario 'usuario'.</p>"



	c = Context({'lista': Response, 'footer': foot})
	renderizado = template.render(c)

	return HttpResponse(renderizado)
