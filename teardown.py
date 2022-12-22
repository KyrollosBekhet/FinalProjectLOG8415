import boto3
from security_group import delete_security_group
from instances import do_terminate
import json
from threading import Thread

def terminate_instances(ec2_resource, ids):
    """
    Terminates all the instances with the given ids
    :param ec2_resource: The ec2_resource used to delete the instance
    :param ids: list of IDs of instances to delete
    """
    threads =[]
    for id in ids:
        thread = Thread(target=do_terminate, args=[ec2_resource, id])
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

"""
Terminate all instances and delete key and security group
"""
session = boto3.Session(profile_name='default')
ec2_client = session.client('ec2')
ec2_resource = session.resource('ec2')
with open("ids.json") as file:
    ids_object = json.load(file)
    terminate_instances(ec2_resource,["Instances_ID"])

    ec2_client.delete_key_pair(KeyName="projectKey")
    delete_security_group(ec2_client, ids_object["security_group_id"])
