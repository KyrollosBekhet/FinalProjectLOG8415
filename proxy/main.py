import json
import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder
import random
import subprocess
import re
import sys

def execute_command(command:str, cluster_dns_object, key):
    """
    Executes the command on a node from the mysql cluster
    :param command: The command to execute
    :param cluster_dns_object: The dictionary that has all the dns of the cluster instances
    :param key: The private ssh key to connect to the instance.
    """
    try:
        print("Executing command: {}".format(command)) 
        if command.lower().find("select") == 0:
            random_number = random.randint(0,10)
            if random_number % 2 == 0:
                random_hit(command, cluster_dns_object, key)

            else:
                custom_hit(command, cluster_dns_object, key)

        else:
            direct_hit(command, cluster_dns_object["master_dns"], key)
    except Exception as e:
        print(e)


def direct_hit(command, master_dns, key):
    send_command(master_dns,command)


def create_ssh_tunnel(data_node_dns, master_node_dns, key):
    """
    Creates an ssh tunnel between the data node and the mangement node
    :param data_node_dns: The DNS of the data node to connect to
    :param master_node_dns: The DNS of the management node that have the musql database
    :param key: The private key used to create the instance. It is used to connect to the instance
    """
    tunnel = SSHTunnelForwarder(
        (data_node_dns, 22),
        ssh_username="ubuntu",
        ssh_pkey=key,
        remote_bind_address= (master_node_dns, 3306)
    )
    tunnel.start()
    return tunnel


def send_command(host, command, tunnel=None):
    """
    Sends a given mySQL command to be executed
    :param host: The host IP or DNS to whom the MySQL connection should be done.
    :param command: The query command to execute
    :param tunnel [optional]: The tunnel previously created to connect to a data node 
    """
    connection =None
    if tunnel is not None:
        connection = pymysql.connect(host=host,
                                    user="testuser", password="t3*5t",
                                    db = 'sakila', port=tunnel.local_bind_port)

    else:
        connection = pymysql.connect(host=host,
                                    user="testuser", password="t3*5t",
                                    db = 'sakila', autocommit=True)
    
    cursor = connection.cursor()
    cursor.execute(command)
    output = cursor.fetchall()
    print(output)
    connection.close()


def random_hit(command, cluster_dns_object, key):
    """
    Sends a command to a random chosen data node
    :param command: The query command to execute on the data node
    :param cluster_dns_object: A dictionary that contains the DNS of the cluster instances
    :param key: The key used to create the insstance 
    """
    data_nodes_dns= [cluster_dns_object["first_data_node_dns"],
                    cluster_dns_object["second_data_node_dns"],
                    cluster_dns_object["third_data_node_dns"]]
    number = random.randint(0,2)
    print("executting random hit with dns: {}".format(data_nodes_dns[number]))
    tunnel = create_ssh_tunnel(data_nodes_dns[number],cluster_dns_object["master_dns"], key)
    send_command("127.0.0.1",command, tunnel=tunnel)
    tunnel.stop()
    tunnel.close()    


def custom_hit(command, cluster_dns_obejct, key):
    """
    Sends a given command to a data node chosen based on the minimal response of a ping compared to the other instances response time.
    :param command: The query command to execute on the data data
    :param cluster_dns_object: A dictionary that contains the DNS of the cluster instances
    :param key: The key used to create the insstance
    """
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
    send_command("127.0.0.1", command, tunnel=tunnel)
    tunnel.stop()
    tunnel.close()



def ping_server(server_dns):
    """
    Send 3 ICMP packets to an instance and extracts the round trip average time statistic returned by the ping command
    :param server_dns: The DNS of the instance to which the packet will be sent
    """
    output = subprocess.check_output(['ping', '-c', '3', server_dns])
    output = output.decode('utf8')
    statistic = re.search(r'(\d+\.\d+/){3}\d+\.\d+', output).group(0)
    avg_time = re.findall(r'\d+\.\d+', statistic)[1]
    response_time = float(avg_time)
    print(response_time)
    return response_time

if __name__ == "__main__":
    """
    The driver used to test the proxy pattern
    """
    cluster_dns_object = None
    with open("dns.json", "r") as file:
        cluster_dns_object = json.load(file)

    pKey = paramiko.RSAKey.from_private_key_file("key.pem")

    # Read the given commands in the argument list
    commands = sys.argv[1:]

    for command in commands:
        execute_command(command, cluster_dns_object, pKey)

