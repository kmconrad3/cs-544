echo "-Xms128M" >> /apache-cassandra-4.0.7/conf/jvm-server.options
echo "-Xmx128M" >> /apache-cassandra-4.0.7/conf/jvm-server.options

sed -i "s/^listen_address:.*/listen_address: "`hostname`"/" /apache-cassandra-4.0.7/conf/cassandra.yaml
sed -i "s/^rpc_address:.*/rpc_address: "`hostname`"/" /apache-cassandra-4.0.7/conf/cassandra.yaml
sed -i "s/- seeds:.*/- seeds: project-5-kc-db-1,project-5-kc-db-2,project-5-kc-db-3/" /apache-cassandra-4.0.7/conf/cassandra.yaml

/apache-cassandra-4.0.7/bin/cassandra -R

sleep infinity

#p5-db-3