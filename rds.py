#*********************************************************************************************************************
# Author - Nirmallya Mukherjee
# This script will connect to a MySQL DB using multiple driver options
#
# Major steps for creating the Private (no public IP) RDS MySQL instance
#   Create a "Dev/Test" / Free MySQL instance
#   Select "Non publicly" available DB
#   DB instance = "flipbasket", UID/PWD = root/password
#   AZ = 2a, create a new SG (name it rds-sg)
#     IMP: When the RDS instance is created check the rds-sg to replace the "inbound" rule IP to the VPC CIDR block of the EC2 instance.
#          Otherwise we will not be able to connect from the EC2 instance
#
# Ubuntu 22.04LTS EC2 T2 micro instance in Oregon for running the py code [dev instance]
#     Open SSH and assign default-sg to the instance
#
# alias python=python3
# sudo apt install python3-pip -y
# sudo pip3 install mysql-connector-python
# wget https://d6opu47qoi4ee.cloudfront.net/employees.sql
#
# mysql -h [RDS end point] -u root -p
#     create database employees;
#     use employees;
#     source employees.sql
#     SELECT emp_no, first_name, last_name, email_id FROM employees limit 10;
#     describe employees;
#     describe orders;
#         Note the column names in a text editor from the output of the above command
#         Close the mysql terminal
#
#*********************************************************************************************************************

import mysql.connector

db_host = 'REPLACE WITH RDS DNS here'
db_username = 'root'
db_password = 'password'
database = 'employees'

# Simple routine to run a query on a database and print the results:
def doQuery(conn) :
    cur = conn.cursor()
    #cur.execute("SELECT [TBD: place any of the employees table columns] FROM employees limit 10")
    #for [TBD: provide any variables here to be accessed by PY seperated by comma] in cur.fetchall() :
    #    print [TBD: use the same PY variables here seperated by comma]
    cur.execute("SELECT emp_no, first_name, last_name, email_id FROM employees limit 10")
    for emp, firstname, lastname, email in cur.fetchall() :
        print(emp, firstname, lastname, email)


def mysqlConnector() :
    print("\n\nUsing mysql.connector")
    print("---------------------")
    conn = mysql.connector.connect(host=db_host, user=db_username, passwd=db_password, db=database)
    doQuery(conn)
    conn.close()


def createOrder() :
    print ("\n\nCreating new record in the orders table")
    conn = mysql.connector.connect(host=db_host, user=db_username, passwd=db_password, db=database)
    cur = conn.cursor()
    # TBD:You have to write this code and submit as part of the lab
    create_order_sql = (
        "insert into orders ("
        " OrderID, OrderUserID, OrderAmount, OrderShipName, OrderShipAddress, OrderShipAddress2,"
        " OrderCity, OrderState, OrderZip, OrderCountry, OrderPhone, OrderFax, OrderShipping,"
        " OrderTax, OrderEmail"
        ") values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    order_data = (
        'ord00111', 16528, 125.50, 'Starfleet Academy', '1225 Audelia drive', '#1971',
        'Fort Baker', 'California', '560102', 'USA', '+91 12345 67890', '+91 55689 66541', 0,
        10.75, 'kirk@starfleet.com'
    )
    cur.execute(create_order_sql, order_data)

    conn.commit()
    cur.close()
    conn.close()


def main() :
    mysqlConnector()
    # Create a sample order record in the order table. This will be used by the advanced version
    createOrder()


main()
