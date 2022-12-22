sudo apt-get update && sudo apt-get  install libncurses5 -y

sudo mkdir -p /opt/mysqlcluster/home

cd /opt/mysqlcluster/home

sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz

sudo tar -xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz

sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

sudo mkdir -p /opt/mysqlcluster/deploy/ndb_data