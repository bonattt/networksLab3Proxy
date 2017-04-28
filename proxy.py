import socket
import sys
import struct
import traceback
import math
import threading

DEBUG = True
HTTP_PORT = 2225
HTTP_HOST = '127.0.0.1'

def main():
    port = HTTP_PORT
    host = HTTP_HOST
    print('starting proxy on port', port)
    sock = welcome_socket(port)
    try:
        run_proxy(sock)
    except Exception as e:
        if DEBUG: print(e)
        # exc_tb = sys.exc_info()[2].tb_lineno
        line_no = sys.exc_info()[2].tb_lineno # exc_tb.tb_lineno
        print("a major error occured on line", line_no, "terminating the proxy server", type(e))
    finally:
        if DEBUG: print("closing welcome socket")
        sock.close()
    input("goodbye!")
    
    
def welcome_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if DEBUG: print("socket created")
    
    server_addr = ('127.0.0.1', port)
    sock.bind(server_addr)
    return sock


def run_proxy(sock):
    sock.listen(5)
    threads = []
    while True:
        connection, client_address = sock.accept()
        print("connection received from", client_address)

        if DEBUG: print('\n' + ('='*20))

        t = threading.Thread(target=handle_connection, args=(connection, client_address))
        threads.append(t)
        t.start()
        # handle_connection(connection, client_address)

        if DEBUG: print('='*20, '\n')

    if DEBUG: print("cleaning up threads")
    for thr in threads:
        thr.join()

    if DEBUG: print("thread cleanup complete")


def handle_connection(client_sock, client_address):
    try:
        data = receive_from(client_sock)
        url = getRequestUrl(data)
        host, port, uri, protocol = parse_url(url)

        # if b'mit' not in host:
        #     print(str(host)[2:-1] + ':' + str(port))
        #     print("##### cancel #####")
        #     return

        if DEBUG: pretty_print_http(data)
        if DEBUG: print('forwarding request to', url)
        if DEBUG: print('client host:', client_address[0])
        if DEBUG: print('client port:', client_address[1])
        if DEBUG: print('protocol:   ', protocol)
        if DEBUG: print('target host:', host)
        if DEBUG: print('target port:', port)
        if DEBUG: print('target uri: ', uri)

        server_sock = open_connection(host, port)
        server_sock.send(data)
        data2 = receive_from(server_sock)
        pretty_print_http(data2)
        print('body:\n', str(get_http_body(data2))[2:-1])
        client_sock.send(data2)

    except Exception as e:
        if DEBUG: print(e)
        line_no = sys.exc_info()[2].tb_lineno # exc_tb.tb_lineno
        traceback.print_tb(sys.exc_info()[2])
        print("a", type(e), "exception occurred on line", line_no, "handling the connection from", client_address)

    finally:
        if DEBUG: print("closing connections")
        server_sock.close()
        client_sock.close()

def get_http_body(http):
    splt = http.split(b'\r\n\r\n')
    return splt[-1]


def get_header_length(http):
    header = http.split(b'\r\n\r\n')[0]
    return len(header)


def get_http_headers(http):
    lines = http.split(b'\n')
    headers = {}
    for line in lines:
        pair = line.split(b': ')
        if len(pair) != 2: continue
        headers[pair[0]] = pair[1]
    return headers


def pretty_print_http(bytes):
    print('http request')
    print('>'*10)
    msg = bytes.split(b'\r\n')
    for line in msg:
        print('\t', str(line)[2:-1])
    print('>'*10)


def get_recv_length(cont_len, head_len):
    recv_len = cont_len - head_len
    recv_len = math.ceil(recv_len / 1024)
    return max(0, recv_len)


def receive_from(sock):
    data = sock.recv(5120) #1024)  #
    headers = get_http_headers(data)
    if b'Content-Length' in headers:
        receive_body(sock, data, headers)

    return data


def receive_body(sock, data, headers):
    head_len = get_header_length(data)
    cont_len = int(headers[b'Content-Length'])
    data += sock.recv(get_recv_length(cont_len, head_len))

    if cont_len != len(data):
        print("WARNING: \n\tcont_len: ", cont_len, "\n\tlen(data):", len(data))

    
def getRequestUrl(req):
    url = req.split()[1]
    return url
    

def open_connection(host, port):

    server_address = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    
    if DEBUG: print("connection to", str(host)[2:]+':'+str(port), "established")
    return sock
    
    
def parse_url(url):
    if b'http://' in url:
        protocol = b'http'
        url = url.replace(b'http://', b'')
    elif b'https://' in url:
        protocol = b'https'
        url = url.replace(b'https://', b'')
    else:
        protocol = None
        
    if b'/' in url:
        index = url.index(b'/')
        hostname = url[:index]
        uri = url[index:]
    else:
        hostname = url
        uri = b''    
    
    if b':' in hostname:
        host, port = hostname.split(b':')
    else:
        host = hostname
        port = b'80'
    return host, int(port), uri, protocol 
    
    
if __name__ == "__main__":
    main()
    