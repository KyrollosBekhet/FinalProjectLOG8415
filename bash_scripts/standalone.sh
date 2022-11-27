sudo apt-get update
sudo apt install mysql-server -y
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xf sakila-db.tar.gz
sudo mysql -e "SOURCE sakila-db/sakila-schema.sql"
sudo mysql -e "SOURCE sakila-db/sakila-data.sql"
sudo apt-get install sysbench -y
sudo sysbench --test=oltp_read_write --mysql-db=sakila --mysql-user=root --table_size=10000 -tabes=23 prepare
sudo sysbench --test=oltp_read_write --mysql-db=sakila --mysql-user=root --table_size=10000 --threads=6 --time=60 run --tables=23 > benchmark_results_standalone.txt
