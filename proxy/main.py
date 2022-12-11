import json
import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder
import random
import subprocess
import re

def execute_command(command:str, cluster_dns_object, key):
    # if select is not at the first so maybe it is a write operation
    print("Executing command: {}".format(command)) 
    if command.lower().find("select") == 0:
        random_number = random.randint(0,10)
        if random_number % 2 == 0:
            random_hit(command, cluster_dns_object, key)

        else:
            custom_hit(command, cluster_dns_object, key)

    else:
        direct_hit(command, cluster_dns_object["master_dns"], key)


def direct_hit(command, master_dns, key):
    tunnel = create_ssh_tunnel(master_dns, master_dns, key)
    send_command(command, tunnel)


def create_ssh_tunnel(data_node_dns, master_node_dns, key):
    tunnel = SSHTunnelForwarder(
        (data_node_dns, 22),
        ssh_username="ubuntu",
        ssh_pkey=key,
        remote_bind_address= (master_node_dns, 3306)
    )
    tunnel.start()
    return tunnel


def send_command(command, tunnel):
    connection =connection = pymysql.connect(host="127.0.0.1",
                                                user="testuser", password="t3*5t",
                                                db = 'sakila', port=tunnel.local_bind_port, autocommit=True)
    
    cursor = connection.cursor()
    cursor.execute(command)
    output = cursor.fetchall()
    print(output)


def random_hit(command, cluster_dns_object, key):
    data_nodes_dns= [cluster_dns_object["first_data_node_dns"],
                    cluster_dns_object["second_data_node_dns"],
                    cluster_dns_object["third_data_node_dns"]]
    number = random.randint(0,2)
    print("executting random hit with dns: {}".format(data_nodes_dns[number]))
    tunnel = create_ssh_tunnel(data_nodes_dns[number],cluster_dns_object["master_dns"], key)
    send_command(command,tunnel)    


def custom_hit(command, cluster_dns_obejct, key):
    dictionary = {}
    time = ping_server(cluster_dns_obejct["first_data_node_dns"])
    dictionary[cluster_dns_obejct["first_data_node_dns"]] = time

    time = ping_server(cluster_dns_obejct["second_data_node_dns"])
    dictionary[cluster_dns_obejct["second_data_node_dns"]] = time

    time = ping_server(cluster_dns_obejct["third_data_node_dns"])
    dictionary[cluster_dns_obejct["third_data_node_dns"]] = time

    minimal_time = min(dictionary.values())
    chosen_data_node_dns = None
    for k,v in dictionary.items():
        if v == minimal_time:
            chosen_data_node_dns = k
    
    print("executing custom hit with dns: {}".format(chosen_data_node_dns))
    tunnel = create_ssh_tunnel(chosen_data_node_dns, cluster_dns_obejct["master_dns"], key)
    send_command(command,tunnel)




def ping_server(server_dns):
    output = subprocess.check_output(['ping', '-c', '3', server_dns])
    output = output.decode('utf8')
    statistic = re.search(r'(\d+\.\d+/){3}\d+\.\d+', output).group(0)
    avg_time = re.findall(r'\d+\.\d+', statistic)[1]
    response_time = float(avg_time)
    return response_time

if __name__ == "__main__":
    
    cluster_dns_object = None
    with open("dns.json", "r") as file:
        cluster_dns_object = json.load(file)

    pKey = paramiko.RSAKey.from_private_key_file("key.pem")

    commands = [
        "SELECT * FROM actor",
        "INSERT INTO actor VALUES (201, 'Kevin', 'Hart', '2006-02-15 04:34:33')",
        "SELECT * FROM actor"
    ]
    for command in commands:
        execute_command(command, cluster_dns_object, pKey)

