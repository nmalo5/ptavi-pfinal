#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class Config(ContentHandler):
    """
    Clase para configurar un User Agent
    """

    def __init__ (self):
        """
        Constructor. Inicializamos las variables
        """
        self.username = ""
        self.passwd = ""
        self.ip_server = "" 
        self.puerto_server = ""
        self.puerto_rtp = ""
        self.ip_proxy = ""
        self.puerto_proxy = ""
        self.path_log = ""
        self.path_audio = ""
        self.lista = []
    def startElement(self, name, attrs):
        """
        Método que se llama cuando se abre una etiqueta xml
        """
        # Tomamos los valores de los atributos
        if name == 'account':
            self.username = attrs.get('username',"")
            self.passwd = attrs.get('passwd',"")
            self.lista += [self.username, self.passwd]
        elif name == 'uaserver':
            self.ip_server = attrs.get('ip',"")
            self.puerto_server = attrs.get('puerto',"")
            self.lista += [self.ip_server, self.puerto_server]
        elif name == 'rtpaudio':
            self.puerto_rtp = attrs.get('puerto',"")
            self.lista += [self.puerto_rtp]
        elif name == 'regproxy':
            self.ip_proxy = attrs.get('ip',"")
            self.puerto_proxy = attrs.get('puerto',"")
            self.lista += [self.ip_proxy, self.puerto_proxy]
        elif name == 'log':
            self.path_log = attrs.get('path',"")
            self.lista += [self.path_log]
        elif name == 'audio':
            self.path_audio = attrs.get('path',"")
            self.lista += [self.path_audio]
    def get_tags(self):
        return self.lista


if __name__ == "__main__":
    """
    Programa principal
    """
    parser = make_parser()
    cHandler = Config()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))
    config_ua = cHandler.get_tags()  
    print config_ua

        #Cliente SIP

    if len(sys.argv) != 4:
        print "SALIENDO"
        sys.exit("Usage: python uaclient.py config method option")
    metodo = sys.argv[2]
    if metodo == "REGISTER":
        expires = int(sys.argv[3])
        print str(expires)
    elif metodo == "INVITE" or metodo == "BYE":
        direccion_sip = sys.argv[3]
        print direccion_sip
        # Dirección IP y puerto del servidor.
    #LOGIN = direccion[0]
    
    USERNAME = config_ua[0]
    if config_ua[2] != "":
        SERVER_IP = config_ua[2]
    else:
        SERVER_IP = "127.0.0.1"
    SERVER_PORT = int(config_ua[3])
    AUDIO_PORT = int(config_ua[4])
    PROXY_IP = config_ua[5]
    PROXY_PORT = int(config_ua[6])
    LOG = config_ua[7]
    FICH = config_ua[8]
        # Contenido que vamos a enviar

        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((PROXY_IP, PROXY_PORT))
    print "CONECTADO"
    
    
   # direccion_SIP = " sip:" + LOGIN + "@" + SERVER_IP +  " SIP/2.0\r\n\r\n"
    if metodo == "REGISTER":
        envio = " sip:" + USERNAME + ":" + str(SERVER_PORT) + " SIP/2.0\r\n"
        envio += "Expires: " + str(expires) + "\r\n\r\n"
    elif metodo == "INVITE": 
        envio = " sip:" + direccion_sip + " SIP/2.0\r\n"
        envio += "Content-type: application/sdp\r\n\r\n"
        envio += "v=0\r\n" + "o=" + USERNAME + " " + SERVER_IP + "\r\n"
        envio += "s=finalptavi\r\n" + "t=0\r\n" 
        envio += "m=audio " + str(AUDIO_PORT) + " RTP\r\n"
    elif metodo == "BYE":
        envio = " sip:" + direccion_sip + " SIP/2.0\r\n"
    envio = metodo + envio 
    print "Enviando: " + envio
    my_socket.send(envio)
    try:
        data = my_socket.recv(1024)
        print 'Recibido -- ', data
        data = data.split()
        print data
        if len(data) > 3:
            if data[0] == "SIP/2.0" and data[8] == "OK":
                rtp_ip = data[13]
                rtp_puerto = data[17]
                metodo = "ACK"
                envio = metodo + " sip:" + direccion_sip + " SIP/2.0\r\n"
                print "Enviando: " + envio
                my_socket.send(envio)
                # Envio rtp
                aEjecutar = ('./mp32rtp -i ' + rtp_ip + ' -p ' + 
                             rtp_puerto + ' < ' + FICH)
                print "Vamos a ejecutar", aEjecutar
                os.system('chmod 755 mp32rtp')
                os.system(aEjecutar)
                print "HECHO"
    except socket.error:
        print ("Error: No server listening at " + SERVER_IP +
               " port " + str(SERVER_PORT))
    #print "Terminando socket..."

    # Cerramos todo
    my_socket.close()
    #print "Fin."
