import boto3
from security_group import delete_security_group
from instances import terminate_instances
import json

"""
Terminate all instances and delete key and security group
"""
session = boto3.Session(profile_name='default')
ec2_client = session.client('ec2')
ec2_resource = session.resource('ec2')
ids_object = json.load("ids.json")
terminate_instances(ec2_resource, ids_object["Instances_ID"])

ec2_client.delete_key_pair(KeyName="projectKey")
delete_security_group(ec2_client, ids_object["security_group_id"])