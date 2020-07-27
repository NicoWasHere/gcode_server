from http.server import HTTPServer, BaseHTTPRequestHandler
import serial
import time
import sys

class Server(BaseHTTPRequestHandler):

    def setPrinter(self,printer,baudrate):
        self.printer = serial.Serial(printer,baudrate)
        self.running = False

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(open("public/index.html").read(), 'utf-8'))

    def do_POST(self):
        #need to provide length so it deosn't hang forever
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        if(self.running):
            self.send_response(409)
            self.wfile.write(str.encode("FAILED"))
            print('nice')
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode("OK"))
            self.sendGcode(str(body).split('\\n'))

    def sendGcode(self,gcode):
        self.running = True
        for line in gcode:
            response = ''
            line = line.split(";")[0]
            if(line != "" and line != "\n"):
                print("line: "+line)
                self.printer.write(str.encode(line+'\n'))
                while response.count("ok") == 0:
                    while self.printer.in_waiting == 0:
                        time.sleep(0.5)
                    response = ''
                    while self.printer.in_waiting > 0:
                        response += str(self.printer.readline())
                    print(response)
        self.running = False

serv = Server
serv.setPrinter(serv,str(sys.argv[1]),int(sys.argv[2]))
httpd = HTTPServer(("localhost", 8080), serv)
httpd.serve_forever()

