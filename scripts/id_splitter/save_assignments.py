import mysql.connector
import dotenv
import os
import csv

from src.find_papers_by_keyword.database import Database

dotenv.load_dotenv()
db_conn = mysql.connector.connect(
    host=os.getenv('ASSIGN_HOST'),
    user=os.getenv('ASSIGN_USER'),
    password=os.getenv('ASSIGN_PASS'),
    database=os.getenv('ASSIGN_DB')
)

database = Database(db_conn)

with open("assignments/20.221.200.122.csv", "r") as file:
    assignment_reader = csv.reader(file)
    next(assignment_reader)
    assignments = [row for row in assignment_reader]

    database.store_publication_fos(assignments)
