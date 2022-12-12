import boto3
from security_group import delete_security_group
import json


# Terminate all instances and delete key and security group

session = boto3.Session(profile_name='default')
ec2_client = session.client('ec2')
ec2_resource = session.resource('ec2')
ids_object = json.load("ids.json")
for id in ids_object["Instances_ID"]:
    instance = ec2_resource.Instance(id)
    instance.terminate()
    instance.wait_until_terminated()

ec2_client.delete_key_pair(KeyName="projectKey")
delete_security_group(ec2_client, ids_object["security_group_id"])