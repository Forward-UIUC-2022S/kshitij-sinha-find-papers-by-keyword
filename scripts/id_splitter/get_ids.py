import json
import mysql.connector
import os
import dotenv

def main():
    dotenv.load_dotenv()
    mag_db = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'), 
        password=os.getenv('MYSQL_PASS'), 
        host="mag-2020-09-14.mysql.database.azure.com", 
        port=3306, 
        database=os.getenv('MYSQL_DB'), 
        ssl_ca="DigiCertGlobalRootCA.crt.pem", 
        ssl_disabled=False
    )

    id_file = "data/PaperIds.json"
    sql = "SELECT PaperId FROM mag_2020_09_14.papers"

    with mag_db.cursor() as cur, open(id_file, "w") as out_file:
        cur.execute(sql)
        ids = cur.fetchall()
        json.dump(ids, out_file)


if __name__ == "__main__":
    main()