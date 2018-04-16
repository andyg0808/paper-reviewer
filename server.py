#!/usr/bin/env python3
import gevent.pywsgi
import gui

server = gevent.wsgi.WSGIServer(('localhost', 5000), gui.app)
server.serve_forever()
