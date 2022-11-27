sudo mkdir -p /opt/mysqlcluster/deploy

cd /opt/mysqlcluster/deploy

sudo mkdir conf

sudo mkdir mysqld_data

cd conf

echo "
[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306" | sudo tee my.cnf

sudo mv ~/config.ini config.ini

cd /opt/mysqlcluster/home/mysqlc
sudo scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data

sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/

