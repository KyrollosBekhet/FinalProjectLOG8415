from threading import Thread


def create_key_pair(ec2_client, key_name):
    """
    Creates a key pair to securely connect to the AWS instances
    :param key_name: The name of the key pair
    :param ec2_resource: The ec2 resource which will create the key pair
    :return: The newly created key_pair
    """
    return ec2_client.create_key_pair(KeyName=key_name)


def create_instances(ec2_resource, image_id, instance_type, key_name, tags, count, security_group_id):
    tag_spec = [
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': tags
                },
            ]
        },
    ]
    monitoring = {
        'Enabled': True,
    }
    instance_params = {
        'ImageId': image_id, 'InstanceType': instance_type,
        'KeyName': key_name, 'SecurityGroupIds': [security_group_id],
        'TagSpecifications': tag_spec, 'Monitoring': monitoring
    }
    instances = ec2_resource.create_instances(**instance_params, MinCount=count, MaxCount=count)

    print(instances)
    return instances


def do_terminate(ec2_resource, instance_id):
    """
    This function terminates an EC2 instance and wait for its state to be terminated.
    :param instance_id: id of the instance to terminate. 
    """
    instance = ec2_resource.Instance(instance_id)
    instance.terminate()
    instance.wait_until_terminated()


def terminate_instances(ec2_resource, instances_ids):
    """
    This function terminates multiple instances simultaniously.
    :param instances_ids: A list of instance id to terminate
    """
    threads = []
    for instance in instances_ids:
        thread = Thread(target=do_terminate, args=[ec2_resource, instance['Id']])
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
