import os
import dotenv
import mysql.connector

def get_azure_mag_db() -> mysql.connector.MySQLConnection:
    dotenv.load_dotenv()
    return mysql.connector.connect(
        user=os.getenv('MAG_USER'), 
        password=os.getenv('MAG_PASS'), 
        host=os.getenv("MAG_HOST"), 
        port=3306, 
        database=os.getenv('MAG_DB'), 
        ssl_ca="DigiCertGlobalRootCA.crt.pem", 
        ssl_disabled=False
    )

def get_forward_db() -> mysql.connector.MySQLConnection:
    dotenv.load_dotenv()
    return mysql.connector.connect(
        host=os.getenv('ASSIGN_HOST'),
        user=os.getenv('ASSIGN_USER'),
        password=os.getenv('ASSIGN_PASS'),
        database=os.getenv('ASSIGN_DB')
    )