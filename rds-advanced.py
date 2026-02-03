#*********************************************************************************************************************
# Author - Nirmallya Mukherjee
# This script will connect to a MySQL DB using multiple driver options & use Redis cache for optimization
# Pre-requisite is the rds.py exercise
#
# Create a Elasticache Redis cluster
#     Configure and create new cluster radio
#     Cluster mode disabled
#     Name = mycache
#     Location = AWS Cloud
#     Disable Multi-AZ and Aito-failover
#     Node type = cache.t2.micro
#     Replicas = 0
#     Create new subnet group; Name = mycache-subnetgroup; VPC = should be the default VPC (same as RDS as well as EC2)
#     Security: select default-sg
#     Disable auto backups, Minor version upgrades
#
# Need to install redis module as follows
#     sudo pip3 install redis
# To check the keys in redis (if redis is running in a docker container) use ->
#     redis-cli keys '*'
#*********************************************************************************************************************

import mysql.connector
import redis
import pickle

#Example elasticache end point can be redis.scsdmx.ng.0001.usw2.cache.amazonaws.com
db_host = 'REPLACE WITH RDS DNS here'
redis_host = 'REPLACE WITH Elasticache primary endpoint DNS here'

db_username = 'root'
db_password = 'password'
database = 'employees'


class Order:
    def __init__(self, orderid, userid, shipping, email):
        self.orderid = orderid
        self.userid = userid
        self.shipping = shipping
        self.email =email
        self.tostring()
    def tostring(self):
        #print(" Order is {0} {1} {2} {3}").format(self.orderid, self.userid, self.shipping, self.email)
        print (" Order is %r %r %r %r" %  (self.orderid, self.userid, self.shipping, self.email))


def getAllOrders() :
    print ("\n\nUsing mysql.connector")
    print ("---------------------")
    conn = mysql.connector.connect(host=db_host, user=db_username, passwd=db_password, db=database)
    cur = conn.cursor()
    cur.execute("SELECT OrderID, OrderUserID, OrderShipName, OrderEmail FROM orders")
    for orderid, userid, shipping, email in cur.fetchall() :
        order_obj = Order(orderid, userid, shipping, email)
    cur.close()
    conn.close()


def getOrder(order_id):
    print ("\nGetting the order", order_id)
    red = redis.StrictRedis(host=redis_host, port=6379, db=0)
    red_obj = red.get(order_id)
    if red_obj != None:
        print ("Object found in cache, not looking in DB")
        #Deserialize the object coming from Redis
        order_obj = pickle.loads(red_obj)
        order_obj.tostring()
    else:
        print ("No key found in redis, going to database to take a look")
        conn = mysql.connector.connect(host=db_host, user=db_username, passwd=db_password, db=database)
        cur = conn.cursor()
        cur.execute("SELECT OrderID, OrderUserID, OrderShipName, OrderEmail FROM orders where OrderID='%s'" % (order_id))
        for orderid, userid, shipping, email in cur :
            order_obj = Order(orderid, userid, shipping, email)
            #Serialize the object
            ser_obj = pickle.dumps(order_obj)
            red.set(order_id, ser_obj)
            print (" Order fetched from DB and pushed to redis")
        cur.close()
        conn.close()


def main() :
    getAllOrders()
    getOrder('ord00111')


main() 		

