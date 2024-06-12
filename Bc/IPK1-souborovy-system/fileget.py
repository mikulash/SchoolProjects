import socket
import sys
import os

def vytvorslozku():
    path = os.path.join(os.getcwd(), "folder")
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print("Folder creation failed")
        exit(1)


def myRecv(sock):
    bufferSize = 4096
    value = bytearray()
    while True:
        packet = sock.recv(bufferSize)
        value.extend(packet)
        if not packet:
            break
    return value


message = 'WHEREIS'
if len(sys.argv) != 5:
    print("malo argumentu")
    exit(1)
else:
    global nameserver
    global surl
    if (sys.argv[1] == '-n') and (sys.argv[3] == '-f'):
        nameserver = sys.argv[2]
        surl = sys.argv[4]
    elif (sys.argv[1] == '-f') and (sys.argv[3] == '-n'):
        nameserver = sys.argv[4]
        surl = sys.argv[2]
    else:
        exit(1)
# zpracovani parametru
parsednames = surl.split("/")
servername = parsednames[2]
filename = parsednames[-1]
if filename == "":
    print("missing filename")
    exit(1)
if len(parsednames) != 4:
    path = parsednames[2:-2]
message = bytes(message + " " + str(servername), "UTF-8")
parsing = nameserver.split(':', 2)
ip = parsing[0]
port = int(parsing[1])
adresa = (ip, port)
# pripojeni na UDP pro NSP--------------------------------
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(message, adresa)
    client.settimeout(2.0)
    data = client.recvfrom(1024)[0]
    data = data.decode("UTF-8")
    data = data.split(' ')
    nalezeno = data[0]
    data = data[1]
    if nalezeno == 'OK':
        fileserver = data.split(':')[1]
    else:
        print("NOT FOUND")
        exit(1)
except socket.timeout:
    print("timeout")
    exit(1)
# pripojeni na TCP--------------------------------------------
fileclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fileMessage = "GET index FSP/1.0\n\ragent: xheinz01\n\rHostname: " + str(servername)
fileMessage = bytes(fileMessage, "UTF-8")
fileserverAdresa = (ip, int(fileserver))
fileclient.connect(fileserverAdresa)
fileclient.sendall(fileMessage)
fileclient.settimeout(5.0)
files = myRecv(fileclient)
fileclient.close()
if filename == 'index':
    vytvorslozku()
    f = open("./folder/" + filename, "w")
    f.write(files.decode("latin-1"))
    print("ALL OK")
    exit(0)

files = files.decode("UTF-8")
files = files.replace('\r\n', ' ')
files = files.split(" ")
count = len(files)
count = count - 5 #pocet souboru bez hlavicky a prazdnych mist v index souboru
# is server ok?
isthere = False
if files[1] != "Success":
    print("NOTHING FOUND")
    exit(1)
for x in files[4:]:
    if x == filename:
        isthere = True
vytvorslozku()
if isthere:
    downloadclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    downloadclient.connect(fileserverAdresa)
    fileMessage = "GET " + filename + " FSP/1.0\n\ragent: xheinz01\n\rHostname: " + str(servername)
    fileMessage = bytes(fileMessage, "latin-1")
    downloadclient.sendall(fileMessage)
    downloadclient.settimeout(5.0)
    file = myRecv(downloadclient)
    downloadclient.close()
    # zapis ziskanych dat
    file = file.decode("latin-1")
    postFile = file.split("\n", 3)[3] #odstrani hlavicku
    postFile = bytes(postFile, "latin-1")
    f = open("./folder/" + filename, "wb")
    f.write(postFile)
    print("ALL OK")
elif filename == '*':
    for x in range(4, 4+count):
        filename = str(files[x])
        jmena = filename.split("/")
        jmeno = jmena[-1]
        cesta = ""
        if len(jmena) != 1:
            cesta = "/".join(jmena[:-1])
            os.makedirs('./folder/'+cesta, exist_ok=True)
        downloadclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        downloadclient.connect(fileserverAdresa)
        fileMessage = "GET " + filename + " FSP/1.0\n\ragent: xheinz01\n\rHostname: " + str(servername)
        fileMessage = bytes(fileMessage, "UTF-8")
        downloadclient.sendall(fileMessage)
        downloadclient.settimeout(5.0)
        file = myRecv(downloadclient)
        downloadclient.close()

        # zapis ziskanych dat
        file = file.decode("latin-1")
        postFile = file.split("\n", 3)[3]  # odstrani hlavicku
        postFile = bytes(postFile, "latin-1")
        f = open("./folder/" + filename, "wb")
        f.write(postFile)
    print("ALL OK")
else:
    print("not there")
    exit(1)
