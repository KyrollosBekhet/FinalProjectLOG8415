sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &
sleep 30
sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgm -e show
cd ~
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xf sakila-db.tar.gz

sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e "CREATE USER 'testuser'@'%' IDENTIFIED BY 't3*5t'"
sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e "GRANT ALL PRIVILEGES ON sakila.* TO 'testuser'@'%'"

sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e "SOURCE sakila-db/sakila-schema.sql"
sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e "SOURCE sakila-db/sakila-data.sql"
sudo apt-get install sysbench -y

hs=`hostname` 

sudo sysbench --test=oltp_read_write --tables=23 --mysql-db=sakila --mysql-host=$hs.ec2.internal --mysql-user=testuser --mysql-password=t3*5t --table_size=10000 prepare


sudo sysbench --test=oltp_read_write --tables=23 --mysql-db=sakila --mysql-host=$hs.ec2.internal --mysql-user=testuser --mysql-password=t3*5t --time=60 --threads=6 --table_size=10000 run > benchmark_cluster.txt