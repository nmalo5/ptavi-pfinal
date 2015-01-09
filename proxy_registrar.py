#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
Clase (y programa principal) para un servidor de registro SIP
"""

import SocketServer
import socket
import sys
import time
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
        self.server_name = ""
        self.server_ip = ""
        self.server_port = "" 
        self.data_path = ""
        self.data_passwd = ""
        self.log_path = ""
        self.lista = []
    def startElement(self, name, attrs):
        """
        Método que se llama cuando se abre una etiqueta xml
        """
        # Tomamos los valores de los atributos
        if name == 'server':
            self.server_name = attrs.get('name',"")
            self.server_ip = attrs.get('ip',"")
            self.server_port = attrs.get('puerto',"")
            self.lista += [self.server_name, self.server_ip, self.server_port]
        elif name == 'database':
            self.data_path = attrs.get('path',"")
            self.data_passwd = attrs.get('passwdpath',"")
            self.lista += [self.data_path, self.data_passwd]
        elif name == 'log':
            self.log_path = attrs.get('path',"")
            self.lista += [self.log_path]
    def get_tags(self):
        return self.lista

class SIPRegisterHandler(SocketServer.DatagramRequestHandler):
    """Register SIP"""

    clientes = {}

    def register2file(self):
        """Escribe en el fichero el diccionario"""
        fichero = "registered.txt"
        fichero = open(fichero, "w")
        cadena = "User\tIP\tPort\tRegistered\tExpires\r\n"
        for cliente in self.clientes.keys():
            expires = self.clientes[cliente][3] #- self.clientes[cliente][2]
            ip = self.clientes[cliente][0]
            port = self.clientes[cliente][1]
            seg_1970_reg = self.clientes[cliente][2]
            cadena += (cliente + "\t" + ip +"\t" + str(port) + "\t" + 
                       str(seg_1970_reg) + "\t" + str(expires) + "\r\n")
       # for cliente in self.clientes.keys():
            #Ponemos la hora en el formato deseado
        #    hora = time.strftime('%Y-%m-%d %H:%M:%S',
         #                        time.gmtime(self.clientes[cliente][1]))
          #  cadena += (cliente + "\t" + self.clientes[cliente][0] +
           #            "\t" + hora + "\r\n")
        #Escribimos el diccionario en el fichero
        fichero.write(cadena)
        fichero.close
    def handle(self):
        """ Registra y borra clientes del server"""
        #self.wfile.write("Hemos recibido tu peticion")
        while 1:
            # Leemos las lineas del fichero
            line = self.rfile.read()
            print line
            if not line:
                break
            palabras = line.split()
            print palabras
            if palabras[0] == "REGISTER":
                direccion = palabras[1]
                direccion = direccion.split(":")
                print direccion
                expires = palabras[4]
                print expires
                direccion_sip = direccion[1]
                port = direccion[2]
                ip = self.client_address[0]
                hora = time.time()
                horalim = time.time() + float(expires)
                # Añadimos una entrada al diccionario
                self.clientes[direccion_sip] = [ip, port, hora, expires]
                print self.clientes[direccion_sip]
                print "SIP/2.0 200 OK \r\n\r\n"
                self.wfile.write("SIP/2.0 200 OK\r\n\r\n")
                # Borramos si el registro ha caducado
                if expires == "0":
                    del self.clientes[(direccion_sip)]
               # for cliente in self.clientes.keys():
                #    if self.clientes[cliente][3] < time.time():
                 #       del self.clientes[cliente]
                self.register2file()
            elif palabras[0] == "INVITE":
                destino = palabras[1]
                destino = destino.split(":")
                destino_sip = destino[1]
                dest_port = ""
                dest_ip = ""
                exito = False
                for cliente in self.clientes.keys():
                    if cliente == destino_sip: 
                        dest_port = self.clientes[destino_sip][1]
                        dest_ip = self.clientes[destino_sip][0]
                        exito = True
                if exito:
                    #ABRIR SOCKET Y ENVIAR
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, 
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((dest_ip, int(dest_port)))
                    print "CONECTADO"
                    my_socket.send(line)
                    #reenviamos al cliente
                    data = my_socket.recv(1024)
                    print data
                    self.wfile.write(data)
                    my_socket.close
                else:
                    self.wfile.write("SIP/2.0 404 User Not Found\r\n\r\n")
                    
            elif palabras[0] == "BYE" or palabras[0] == "ACK":
                destino = palabras[1]
                destino = destino.split(":")
                destino_sip = destino[1]
                dest_port = ""
                dest_ip = ""
                exito = False
                for cliente in self.clientes.keys():
                    if cliente == destino_sip: 
                        dest_port = self.clientes[destino_sip][1]
                        dest_ip = self.clientes[destino_sip][0]
                        exito = True
                print exito
                #if palabras[0] == "BYE":
                 #   del self.clientes[(direccion_sip)]
                if exito:
                    #ABRIR SOCKET Y ENVIAR
                    print "REENVIAMOS 200 OK"
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, 
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((dest_ip, int(dest_port)))
                    print "CONECTADO"
                    my_socket.send(line)
                     #reenviamos al cliente
                    data = my_socket.recv(1024)
                    print data
                    self.wfile.write(data)
                    my_socket.close
               
                
            elif palabras[0] == "CANCEL" or palabras[0] == "OPTIONS":
                self.wfile.write("SIP/2.0 405 Method Not Allowed\r\n\r\n")
            else:
                self.wfile.write("SIP/2.0 400 Bad Request\r\n\r\n")

if __name__ == "__main__":
    """ Creamos servidor SIP y escuchamos"""
    parser = make_parser()
    cHandler = Config()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))
    config_ua = cHandler.get_tags()  
    print config_ua
    SERVER_NAME = config_ua[0]
    SERVER_IP = config_ua[1]
    SERVER_PORT = int(config_ua[2])
    DATA_PATH = config_ua[3]
    DATA_PSSWDPATH = config_ua[4]
    LOG_PATH = config_ua[5]
    serv = SocketServer.UDPServer(("", SERVER_PORT), SIPRegisterHandler)
    print "Lanzando servidor register..."
    serv.serve_forever()
