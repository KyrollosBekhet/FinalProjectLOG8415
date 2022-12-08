"""
import socket
from threading import Thread
import sys

def start():
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 3000))
        server_sock.listen(100)
        print("[*] Server started successfully on port: 3000")
        while True:
            (client_socket, client_address) = server_sock.accept()
            data = client_socket.recv(1024)
            print(data)
            start_threading(client_socket, data, client_address)

    except Exception as e:
        print(e)
        sys.exit(2) 


def start_threading(conn, data, addr):
    t = Thread(connection_string, (conn, data, addr))
    t.start()

def connection_string(conn, data, addr):
    pass

def proxy_server(hostname, port, conn, addr, data):
    try:
        print(data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        sock.send(data)
        while 1:
            reply = sock.recv(1024)
            if(len(reply)>0):
                conn.send(reply)
                
                dar = float(len(reply))
                dar = float(dar/1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                print("[*] Request Done: %s => %s <=" % (str(addr[0]), str(dar)))

            else:
                break;

        sock.close()
        conn.close()

    except socket.error:
        sock.close()
        conn.close()

if __name__ == "__main__":
    start()

"""
import pymysql

def mysqlconnect():
    # To connect MySQL database
    conn = pymysql.connect(
        host='ip-172-31-28-163.ec2.internal',
        user='testuser',
        password = "t3*5t",
        db='sakila',
        bind_address="ip-172-31-21-198.ec2.internal",
        )

    cur = conn.cursor()

    # Select query
    cur.execute("select * actor")
    output = cur.fetchall()

    for i in output:
        print(i)

    # To close the connection
    conn.close()

if __name__ == "__main__":
    mysqlconnect()
