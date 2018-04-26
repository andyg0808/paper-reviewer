#!/usr/bin/env python3
from gevent.pywsgi import WSGIServer
import gui

server = WSGIServer(('localhost', 5000), gui.app)
server.serve_forever()
