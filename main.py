import boto3
from instances import *
from security_group import *
from ssh_connection import *
import os

session = boto3.Session(profile_name='default')
ec2_client = session.client('ec2')
ec2_resource = session.resource('ec2')

vpcs = ec2_client.describe_vpcs()
vpc_id = vpcs.get('Vpcs', [{}])[0].get('VpcId', '')

instance_ami = 'ami-08c40ec9ead489470'
#key_pair = ec2_client.describe_key_pairs()['KeyPairs'][0]
key_pair = create_key_pair(ec2_client, "projectKey")
key_material = key_pair["KeyMaterial"]
security_group_id = create_security_group(ec2_client, vpc_id)['GroupId']
instances = []

try:
    # do the steps for the standalone version
    instance = create_instances(ec2_resource, instance_ami, "t2.micro", key_pair["KeyName"], "standalone_instance", 1,
                                security_group_id)[0]
    instance.wait_until_running()
    print(instance.id)
    instance = ec2_resource.Instance(instance.id)
    print(instance)
    instances.append(instance)
    standalone_public_ip = instance.public_ip_address
    folder_path = os.path.abspath("bash_scripts")
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


except Exception as e:
    print(e)

finally:
    if len(instances) > 0:
        for instance in instances:
            instance.terminate()
            instance.wait_until_terminated()

    ec2_client.delete_key_pair(KeyName="projectKey")
    delete_security_group(ec2_client, security_group_id)
