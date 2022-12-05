"""
[ndb_mgmd] 
hostname=ip-172-31-88-28.ec2.internal
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1
[ndbd default]
noofreplicas=1
[ndbd]
hostname=ip-172-31-91-195.ec2.internal
nodeid=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[mysqld]
nodeid=50
"""
import os


def write_file_content(mgmt_node_hs, first_slave_hs, second_slave_hs, third_slave_hs):
    ret = "[ndb_mgmd]\n" +\
          "hostname={}\n".format(mgmt_node_hs) +\
          "datadir=/opt/mysqlcluster/deploy/ndb_data\n" +\
          "nodeid=1\n"\
          + "[ndbd default]\n" \
          + "noofreplicas=3\n" \
          + "[ndbd]\n" \
          + "hostname={}\n".format(first_slave_hs) \
          + "nodeid=3\n" \
          + "datadir=/opt/mysqlcluster/deploy/ndb_data\n"\
          + "[ndbd]\n" \
          + "hostname={}\n".format(second_slave_hs) \
          + "nodeid=4\n" \
          + "datadir=/opt/mysqlcluster/deploy/ndb_data\n" \
          + "[ndbd]\n" \
          + "hostname={}\n".format(third_slave_hs) \
          + "nodeid=5\n" \
          + "datadir=/opt/mysqlcluster/deploy/ndb_data\n" \
          + "[mysqld]\n"\
          + "nodeid=50" 
    print(ret)
    path_folder = os.path.curdir
    path_file = os.path.join(path_folder, 'config.ini')
    f = open(path_file, "w")
    f.write(ret)
    f.close()


if __name__ == "__main__":
    write_file_content("ip-172-31-88-28.ec2.internal", "ip-172-31-91-195.ec2.internal", "ip-172-31-91-195.ec2.internal", "ip-172-31-91-195.ec2.internal")
