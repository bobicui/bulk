#!/usr/bin/python
#Function: insert a batch of records to db.
import sys
import os
import string
import re
import MySQLdb

if len(sys.argv) < 2 or (not os.path.isfile(sys.argv[1])):
    print "Usage: bulk.py file"
    print "       file: the file that store the mysql connection and record info"
    sys.exit()

file_name = sys.argv[1]
file = open(file_name, 'r')

line = file.readline()
if line.find("database:") == -1:
    print "error: the line 1 must be like 'database: db_name'"
    sys.exit()
database = line.split(":")[1].strip()[1:-1]

line = file.readline()
if line.find("table:") == -1:
    print "error: the line 2 must be like 'table: table_name
    sys.exit()
table = line.split(":")[1].strip()[1:-1]

line = file.readline()
if line.find("hostname:") == -1:
    print "error: the line 3 must be like 'hostname: localhost'"
    sys.exit()
hostname = line.split(":")[1].strip()[1:-1]

line = file.readline()
if line.find("username:") == -1:
    print "error: the line 4 must be like 'username: root'"
    sys.exit()
username = line.split(":")[1].strip()[1:-1]

line = file.readline()
if line.find("password:") == -1:
    print "error: the line 5 must be like 'password: 123456'"
    sys.exit()
password = line.split(":")[1].strip()[1:-1]

line = file.readline()
if line.find("port:") == -1:
    print "error: the line 6 must be like 'password: 3306'"
    sys.exit()
port = line.split(":")[1].strip()[1:-1]

line = file.readline()
if line.find("charset:") == -1:
    print "error: the line 5 must be like 'password: utf8'"
    sys.exit()
chset = line.split(":")[1].strip()[1:-1]

db = MySQLdb.connect(host=hostname, user=username, passwd=password, db=database, charset=chset)

sql = "insert into " + table + " set "
line = file.readline()
ranges = {}
while line:
    line = line.strip()
    field = line.split(":")[0]
    value = line.split(":")[1]
    if value.find("range") != -1:
	ranges[field] = value[len("range")+2:-1]
    else:
        sql += field + "=" + value + ","
    line = file.readline()

ranges_content = {}
if ranges:
    #get all ranges to one dictionary, the key is the field, the value is a array that contains the all the possible values 
    for (k, v) in ranges.items():
	ranges_content[k] = []
        if v.find("~") != -1:
	    value_list = v.split("~")
	    if value_list[1] == "":
		ranges_content[k].append(value_list[0] + "+")
	    else:
		print value_list[0] + "," + value_list[1]
		for value in range(int(value_list[0]), int(value_list[1])+1):
		    ranges_content[k].append(str(value))	
        else:
	    file_name = v[1:-1]
            f = open(file_name, 'r')
            content = f.read()
            value_list = content.split(" ")
	    for index, value in enumerate(value_list):
		value_list[index] = "'" + value + "'"
	    ranges_content[k] = value_list

    count_in_range = 0
    #check the quantity in all ranges, if the quantity is not equal, exit the program
    for (k, v_list) in ranges_content.items():
	if count_in_range == 0 and len(v_list) > 1:
	    count_in_range = len(v_list)	
	elif count_in_range > 1 and len(v_list) > 1 and len(v_list) != count_in_range:
	    print str(count_in_range) + "," + str(len(v_list))
	    print "The quantity in ranges are not equal!"
	    sys.exit()

    #fill the same quantity of number to the ranges that has no range end
    for (k, v_list) in ranges_content.items():
	if count_in_range == 1 and v_list[0].find("+") != -1:
	    print "The situation which has just one range and this range has no range end is not allowed!"
	    sys.exit()
	elif v_list[0].find("+") != -1:
	    ranges_content[k] = []
	    range_start = int(v_list[0].rstrip("+"))
	    for value in range(range_start, range_start + count_in_range):
                    ranges_content[k].append(str(value))
    #insert to db
    count = 0
    while count < count_in_range:
	sql1 = sql
        for (k, v_list) in ranges_content.items():
	    sql1 += k + "=" + v_list[count] + ","
	sql1 = sql1.rstrip(",")
	result = cursor.execute(sql1)
	if result >= 1:
            print "[ " + sql1 + " ] succeed"
	count += 1
else:
    sql1 = sql.rstrip(",")
    result = cursor.execute(sql1)
    if result >= 1:
        print "[ " + sql1 + " ] succeed"

db.close()
