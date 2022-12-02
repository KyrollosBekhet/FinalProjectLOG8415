import time
import boto3


def create_security_group(ec2, vpc_id):
    """
    This method creates the security group and adds the inbound and outbound rules necessary.

    :param ec2: The ec2 resource that we can get from boto3
    :return: {
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "UserIdGroupPairs": []
                }
            ],
            "Description": "My security group"
            "IpPermissions": [],
            "GroupName": "my-sg",
            "VpcId": "vpc-1a2b3c4d",
            "OwnerId": "123456789012",
            "GroupId": "sg-903004f8"
        }
    """
    security_group = ec2.create_security_group(
        Description="security group TP1",
        GroupName="TP1automaticSG",
        VpcId=vpc_id
    )

    add_outbound_rules(ec2, security_group['GroupId'])
    add_inbound_rules(ec2, security_group['GroupId'])

    return security_group


def add_inbound_rules(ec2, security_group_id):
    # ingress_rules
    """
    The rules accepted from incoming traffic will correspond to SSH, HTTP and HTTPS
    :param security_group: The security group to which we want to add rules
    :return: nothing
    """
    ip_permission = [{
        'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }, {
        'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }, {
        'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }]

    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=ip_permission)


def add_outbound_rules(ec2, security_group_id):
    # egress_rules
    """
    The rules accepted to go to the outside traffic will be HTTP and HTTPS
    AWS adds also a default all traffic rule
    :param security_group: The security group to which we want to add rules
    :return: nothing
    """
    ip_permission = [{
        'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }, {
        'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }]

    ec2.authorize_security_group_egress(
        GroupId=security_group_id,
        IpPermissions=ip_permission)


def delete_security_group(ec2, security_group_id):
    """
    This function remove a security group
    :security_group_id : The security group to delete
    """
    ec2.delete_security_group(GroupId=security_group_id)


if __name__ == "__main__":
    """
    This code sample is provided to execute this file from the command line without running the main.py.
    """
    ec2_client = boto3.client('ec2')

    response = ec2_client.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    security_group = create_security_group(ec2_client, vpc_id)

    print(security_group['GroupId'])

    # The sleep is placed to simulate an interruption
    time.sleep(60)

    delete_security_group(ec2_client, security_group['GroupId'])
