"""Get Keyword JSON

Script used to get keyword data from a database and store it in the following JSON format:
    [
        {
            "id": int,
            "keyword": str
        },
        ...
    ]

* This script may not be required in the future. It is being used now because MAG
embeddings are being generated on an Azure server that does not have access to the 
Forward databse. To get around this, the keyword data is extracted into a file and
moved to the Azure server so the server doesn't have to rely on a Forward database.
"""

import json
import os
import dotenv
import sys
import mysql.connector

json_filepath = "data/db_keywords.json"

dotenv.load_dotenv()
db_conn = mysql.connector.connect(
    host=os.getenv('ASSIGN_HOST'),
    user=os.getenv('ASSIGN_USER'),
    password=os.getenv('ASSIGN_PASS'),
    database=os.getenv('ASSIGN_DB')
)

sql = "SELECT id, keyword FROM FoS"

with db_conn.cursor(dictionary = True) as cur, \
     open(json_filepath, "w") as json_file:

     print("Fetching keywords from database")
     cur.execute(sql)
     keywords = cur.fetchall()

     print(keywords[:10])

     print(f"Saving {len(keywords)} keywords to {json_filepath}")
     json.dump(keywords, json_file)
     
