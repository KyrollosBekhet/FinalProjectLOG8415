import json
import os

def generate_dns_file(master_dns, first_data_node_dns, second_data_node_dns, third_data_node_dns):
    """
    Generates a json file with the hostnames of the instances of the cluster
    :param master_dns: The hostname of the master node
    :param first_data_node_dns: The hostname of the first data node
    :param second_data_node_dns: the hostname of the second data node
    :param third_data_node_dns: The hostname of the third data node
    """
    dictionary = {
        "master_dns":master_dns,
        "first_data_node_dns": first_data_node_dns,
        "second_data_node_dns": second_data_node_dns,
        "third_data_node_dns": third_data_node_dns,
    }
    path_folder = os.path.abspath("proxy")
    path_file = os.path.join(path_folder, "dns.json")
    with open(path_file, "w") as output_file:
        json.dump(dictionary, output_file)

def generate_pem_file(key):
    """
    Writes the key used to connect to the instances in a pem file
    :param key: The private key used to connect to the instances
    """
    path_folder = os.path.abspath("proxy")
    path_file = os.path.join(path_folder, "key.pem")
    with open(path_file, "w") as output:
        output.write(key)

def generate_ids_file(instances, security_group_id):
    """
    Writes the ids in a JSON file used later to delete the instances
    :param instances: The ec2 instances created
    :param security_group_id: The id of the security group created
    """
    ids = []
    for instance in instances:
        ids.append(instance.id)
    
    dictionary = {
        "Instances_ID": ids,
        "security_group_id": security_group_id
    }
    file_name = "ids.json"
    with open(file_name, "w") as file:
        json.dump(dictionary, file)

if __name__ == "__main__":
    generate_dns_file("ip-172-31-90-227.ec2.internal", "ip-172-31-81-129.ec2.internal", "ip-172-31-93-215.ec2.internal", "ip-172-31-84-174.ec2.internal")
    path_folder = os.path.abspath("proxy")
    path_file = os.path.join(path_folder, "dns.json")
    json_obj = None
    with open(path_file, "r") as file:
        json_obj = json.load(file)
    
    print(json_obj)
