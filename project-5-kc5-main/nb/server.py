from concurrent import futures

import grpc

import station_pb2
import station_pb2_grpc
import cassandra

from cassandra.cluster import Cluster, ConsistencyLevel
from cassandra.query import SimpleStatement
import pandas as pd

try:
    cluster = Cluster(['project-5-kc-db-1', 'project-5-kc-db-2', 'project-5-kc-db-3'])
    cass = cluster.connect()
except Exception as e:
    print(e)
    
cass.execute("drop keyspace if exists weather")
cass.execute("create keyspace weather with replication = {'class': 'SimpleStrategy', 'replication_factor': 3}")
cass.execute("use weather")
cass.execute("create type station_record (tmin int, tmax int)")
(cass.execute("""
    CREATE TABLE stations (
        id text,
        name text STATIC, 
        date date, 
        record weather.station_record,
        PRIMARY KEY (id, date)
    )
    WITH CLUSTERING ORDER BY (date ASC)
"""))

class Station(station_pb2_grpc.StationServicer):
    def RecordTemps(self, request, context):
        global cass
        station = request.station
        date = request.date
        tmin = request.tmin
        tmax = request.tmax
        print("Before")
        insert_statement = cass.prepare("INSERT INTO weather.stations (id, date, record) VALUES (?, ?, { tmin: ?, tmax: ?})")
        insert_statement.consistency_level = ConsistencyLevel.ONE
        print("Made it here")
        try:
            cass.execute(insert_statement, (station, date, tmin, tmax))
            return station_pb2.RecordTempsReply()
        except Exception as e:
            return station_pb2.RecordTempsReply(error="Value error")


    def StationMax(self, request, context):
        global cass
        station = request.station
        max_statement = cass.prepare("SELECT MAX(record.tmax) FROM weather.stations WHERE id = ?")
        max_statement.consistency_level = ConsistencyLevel.THREE

        try:
            result = cass.execute(max_statement, [station])
            maxTemp = int(pd.DataFrame(result).iloc[0]["system_max_record_tmax"])
            return station_pb2.StationMaxReply(tmax=maxTemp)
        except Exception as e:
            return station_pb2.StationMaxReply(error="No temperature data found for station")

        

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    station_pb2_grpc.add_StationServicer_to_server(Station(), server)
    server.add_insecure_port('[::]:5440')
    server.start()
    print("start listening on port 5440...")
    server.wait_for_termination()


if __name__ == '__main__':
    server()