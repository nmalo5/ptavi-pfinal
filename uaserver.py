#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor SIP
"""

import SocketServer
import sys
import os
from uaclient import Config
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class Server_Sip(SocketServer.DatagramRequestHandler):
    """
    Clase para un Servidor SIP
    """
    receptor = {'IP': "", "PORT": 0}
    print "entrada" 
    
    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            #SIP/2.0 200 OK\r\n\r\n
            line = self.rfile.read()
            line = line.split()
            if not line:
                break
            print line 
            # Si no hay más líneas salimos del bucle infinito
            if line[0] == "INVITE":
                print "INVITE recibido"
                self.receptor["IP"] = line[7]
                self.receptor["PORT"] = line[11]
                print self.receptor["IP"]
                print self.receptor["PORT"]
                mensaje = ("SIP/2.0 100 Trying\r\n\r\nSIP/2.0 180 Ringing"
                           "\r\n\r\nSIP/2.0 200 OK\r\n")
                mensaje += "Content-type: application/sdp\r\n\r\n"
                mensaje += "v=0\r\n" + "o=" + USERNAME + " " + SERVER_IP + "\r\n"
                mensaje += "s=finalptavi\r\n" + "t=0\r\n" 
                mensaje += "m=audio " + str(AUDIO_PORT) + " RTP\r\n"
                self.wfile.write(mensaje)
            elif line[0] == "ACK":
                print "ACK recibido"
                print self.receptor["IP"]
                print self.receptor["PORT"]
            # aEjecutar es un string con lo que se ha de ejecutar en la shell
                aEjecutar = ('./mp32rtp -i ' + self.receptor["IP"] + ' -p ' + 
                             self.receptor["PORT"] + ' < ' + fich)
                print "Vamos a ejecutar", aEjecutar
                os.system('chmod 755 mp32rtp')
                os.system(aEjecutar)
                print "HECHO"
            elif line[0] == "BYE":
                print "BYE recibido"
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
            elif (line[0] == "CANCEL" or line[0] == "REGISTER"
                  or line[0] == "OPTIONS"):
                print "metodo no disponible recibido"
                self.wfile.write("SIP/2.0 405 Method Not Allowed\r\n\r\n")
            else:
                print "petición incorrecta recibida"
                self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")

if __name__ == "__main__":
    parser = make_parser()
    cHandler = Config()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))
    config_ua = cHandler.get_tags()  
    print config_ua
    USERNAME = config_ua[0]
    if len(sys.argv) != 2:
        sys.exit("Usage: python uaserver.py config")
    else:
        print "Listening..."
    # Creamos servidor sip y escuchamos
    audiortp_port = config_ua[4]
    fich = config_ua[8]
    SERVER_IP = config_ua[2]
    SERVER_PORT = int(config_ua[3])
    AUDIO_PORT = int(config_ua[4])
    PROXY_IP = config_ua[5]
    PROXY_PORT = int(config_ua[6])
    serv = SocketServer.UDPServer((SERVER_IP, SERVER_PORT), Server_Sip)
    print "Lanzando servidor SIP..."
    serv.serve_forever()
