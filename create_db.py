import pymysql

my = pymysql.connect(
    host="localhost",
    user="root",
    passwd="root")

my_cursor = my.cursor()

my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
	print(db)