Pyntas
======

Proyecto participante en el FOSS de la Euskal Encounter 20 realizado en aproximadamente 12h.

* Autor: Jorge Bastida
* Email: me@jorgebastida.com
* Sitio: AO-40

Tecnología utilizada
--------------------
* Python
* Redis
* Tornado
* Websockets
* Raphaël JS

Features
--------

* Pyntas es un monitor en tiempo real de todos los mensajes de chat que se publican en el chat del DC de la Euskal Party y que continen una referencia a un puesto.
* De igual manera permite crear listas publicas que contengan información sobre infractores de las normas o simplemente de puestos con ordenadores chulos y dignos de ir a visitar.

Captura de mensajes
-------------------
Para la captura de mensajes ha sido necesario construir un bot ``dcbot.py`` que captura todos los mensajes que se publican en el chat. A continucación se busca información sobre el puesto del usuario, e.j: ``AO-40``, ``AO 40`` o ``AO40``. Si el mensaje contiene alguna de estas candenas se publica el mensaje en una cola de redis utilizando ``pub/sub``.

Monitor
-------
El monitor se ha implementado utilizando Tornado y websockets. El monitor consume la lista de mensajes desde redis y notifica a todos los navegadores la presencia de un nuevo mensaje a mostrar utilizado websockets.


Instalación (Pip + virtualenv)
------------------------------

1. Crear un virtualenv::

    $ virtualenv pyntasve

2. Activar el virtualenv::

    $ source pyntasve/bin/activate

3. Clonar el proyecto.

4. Instalar REQUIREMENTS::

    $ pip install -r REQUIREMENTS pyntas/REQUIREMENTS

6. Instalar y arrancar una instacia de redis.

7. Arrancar el Bot de DC::

    $ python dcbot NICK-DEL-BOT

8. Arrancar tornado::

    $ python server.py

9. Visitar http://127.0.0.1:8888

Capturas
--------

.. image:: https://github.com/jorgebastida/pyntas/raw/master/static/screenshot.png
