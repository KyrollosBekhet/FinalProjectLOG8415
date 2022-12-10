import json
import os

def generate_dns_file(master_dns, first_data_node_dns, second_data_node_dns, third_data_node_dns):
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
    path_folder = os.path.abspath("proxy")
    path_file = os.path.join(path_folder, "key.pem")
    with open(path_file, "w") as output:
        output.write(key)


if __name__ == "__main__":
    generate_dns_file("ip-172-31-90-227.ec2.internal", "ip-172-31-81-129.ec2.internal", "ip-172-31-93-215.ec2.internal", "ip-172-31-84-174.ec2.internal")
    path_folder = os.path.abspath("proxy")
    path_file = os.path.join(path_folder, "dns.json")
    json_obj = None
    with open(path_file, "r") as file:
        json_obj = json.load(file)
    
    print(json_obj)
