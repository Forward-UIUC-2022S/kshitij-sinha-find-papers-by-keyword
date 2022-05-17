import os
import csv

from src.find_papers_by_keyword.database import Database
import src.database.db_conn_factory as db_factory

assignments_dir = "assignments"
db_conn = db_factory.get_forward_db()
database = Database(db_conn)

for filename in os.listdir(assignments_dir):
    filepath = os.path.join(assignments_dir, filename)
    
    print("Saving assignments from ", filepath)
    with open(filepath, "r") as file:
        assignment_reader = csv.reader(file)
        next(assignment_reader)
        assignments = [row for row in assignment_reader]

        database.store_publication_fos(assignments)
