import sqlite3


## connect to sqlite3
connection = sqlite3.connect("student.db")

## create a cursor object to insert record, create table
cursor = connection.cursor()

## Create the table
table_info = """
create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25),
MARKS INT)
"""

cursor.execute(table_info)

## Insert some more records
cursor.execute('''Insert Into STUDENT values('Rahul','Data Science','A',90)''')
cursor.execute('''Insert Into STUDENT values('John','Data Science','B',100)''')
cursor.execute('''Insert Into STUDENT values('Mukesh','Data Science','A',86)''')
cursor.execute('''Insert Into STUDENT values('Jacob','DEVOPS','A',50)''')
cursor.execute('''Insert Into STUDENT values('Dipesh','DEVOPS','A')''')

## Display all the records
print("The Inserted records are ")
data = cursor.execute("""select * from STUDENT """)
for row in data:
    print(row)

## commit the changes in the database

connection.commit()
connection.close()