import boto3
from instances import *
from security_group import *
from ssh_connection import *
from config_file_writter import *
import os
from proxy_files_generator import *

session = boto3.Session(profile_name='default')
ec2_client = session.client('ec2')
ec2_resource = session.resource('ec2')

vpcs = ec2_client.describe_vpcs()
vpc_id = vpcs.get('Vpcs', [{}])[0].get('VpcId', '')

sn_all = ec2_client.describe_subnets()
subnets = []
for sn in sn_all['Subnets']:
    if sn['AvailabilityZone'] == 'us-east-1d':
        subnets.append(sn['SubnetId'])

instance_ami = 'ami-08c40ec9ead489470'
#key_pair = ec2_client.describe_key_pairs()['KeyPairs'][0]
key_pair = create_key_pair(ec2_client, "projectKey")
key_material = key_pair["KeyMaterial"]
generate_pem_file(key_material)
security_group_id = create_security_group(ec2_client, vpc_id)['GroupId']
instances = []

try:
    folder_path = os.path.abspath("bash_scripts")
    
    # do the steps for the standalone version
    instance = create_instances(ec2_resource, instance_ami, "t2.micro", key_pair["KeyName"], "standalone_instance", subnets[0], 1,
                                security_group_id)[0]
    instance.wait_until_running()
    print(instance.id)
    instance = ec2_resource.Instance(instance.id)
    print(instance)
    instances.append(instance)
    standalone_public_ip = instance.public_ip_address

    # standalone benchmarking
    files = [os.path.join(folder_path, "standalone.sh")]
    time.sleep(60)
    standalone_connection = instance_connection(standalone_public_ip, key_material)
    commands = [
        "chmod 777 standalone.sh",
        "./standalone.sh"
    ]
    transfer_file(standalone_connection, files)
    run_commands(standalone_connection, commands)
    get_file_from_remote(standalone_connection, "benchmark_results_standalone.txt")
    close_connection(standalone_connection)

    #cluster benchmarking
    master_node_instance = create_instances(ec2_resource, instance_ami, "t2.micro", key_pair["KeyName"], "master_node", subnets[0], 1,
                                security_group_id)[0]
    master_node_instance.wait_until_running()
    master_node_instance = ec2_resource.Instance(master_node_instance.id)
    instances.append(master_node_instance)

    proxy_server = create_instances(ec2_resource, instance_ami, "t2.large", key_pair["KeyName"], "proxy_server", subnets[0], 1,
                                security_group_id)[0]
    proxy_server.wait_until_running()
    proxy_server = ec2_resource.Instance(proxy_server.id)
    instances.append(proxy_server)

    cluster_slaves = []
    slave_nodes = create_instances(ec2_resource, instance_ami, "t2.micro", key_pair["KeyName"], "slave_node", subnets[0], 3,
                                security_group_id)
    for node in slave_nodes:
        node.wait_until_running()
        ins = ec2_resource.Instance(node.id)
        instances.append(ins)
        cluster_slaves.append(ins)

    write_file_content(master_node_instance.private_dns_name, cluster_slaves[0].private_dns_name,
        cluster_slaves[1].private_dns_name, cluster_slaves[2].private_dns_name)

    generate_dns_file(master_node_instance.private_dns_name, cluster_slaves[0].private_dns_name,
        cluster_slaves[1].private_dns_name, cluster_slaves[2].private_dns_name)

    time.sleep(60)
    master_connection = instance_connection(master_node_instance.public_ip_address, key_material)
    first_slave_connection = instance_connection(cluster_slaves[0].public_ip_address, key_material)
    second_slave_connection = instance_connection(cluster_slaves[1].public_ip_address, key_material)
    third_slave_connection = instance_connection(cluster_slaves[2].public_ip_address, key_material)
    slave_connections = [first_slave_connection, second_slave_connection, third_slave_connection]

    files = [
        os.path.join(folder_path, "clusterCommonSteps.sh"),
        os.path.join(folder_path, "clusterBenchmarking.sh"),
        os.path.join(folder_path, "clusterMgmtNodeSteps.sh"),
        os.path.join(os.path.curdir, "config.ini")
    ]
    transfer_file(master_connection, files)
    commands = [
        "chmod 777 clusterCommonSteps.sh clusterBenchmarking.sh clusterMgmtNodeSteps.sh",
        "./clusterCommonSteps.sh",
        "./clusterMgmtNodeSteps.sh"
    ]
    run_commands(master_connection, commands)
    
    files = [
        os.path.join(folder_path, "clusterCommonSteps.sh"),
    ]

    commands = [
        "chmod 777 clusterCommonSteps.sh",
        "./clusterCommonSteps.sh",
        "sudo /opt/mysqlcluster/home/mysqlc/bin/ndbd -c {}:1186".format(master_node_instance.private_dns_name)
    ]
    time.sleep(60)
    for connection in slave_connections:
        transfer_file(connection, files)
        run_commands(connection, commands)

    commands = [
        "./clusterBenchmarking.sh"
    ]
    run_commands(master_connection, commands)
    get_file_from_remote(master_connection, "benchmark_cluster.txt")

    close_connection(master_connection)
    for connection in slave_connections:
        close_connection(connection)

    proxy_connection = instance_connection(proxy_server.public_ip_address, key_material)
    folder_path = os.path.abspath("proxy")
    files = [
        os.path.join(folder_path, "main.py"),
        os.path.join(folder_path, "setup.sh"),
        os.path.join(folder_path, "dns.json"),
        os.path.join(folder_path, "key.pem")
    ]
    transfer_file(proxy_connection, files)
    commands= [
        "chmod 777 setup.sh",
        "./setup.sh",
    ]
    run_commands(proxy_connection, commands)



except Exception as e:
    print(e)

finally:
    """
    if len(instances) > 0:
        for instance in instances:
            instance.terminate()
            instance.wait_until_terminated()

    ec2_client.delete_key_pair(KeyName="projectKey")
    delete_security_group(ec2_client, security_group_id)
    """