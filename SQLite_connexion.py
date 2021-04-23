import sqlite3
from sqlite3 import Error

def ConnectSQL(filename):

	

	#Connection to de DB file:
	try:
		conn = sqlite3.connect(filename)
		mycursor = conn.cursor()
		print("Connected to the Database\n")


		mycursor.execute("SELECT packet FROM 'packets'")
		Car_Data = mycursor.fetchall()
		
		return Car_Data

	except Error as e:
		print(e)
		print("Error from ConnectSQL:")



