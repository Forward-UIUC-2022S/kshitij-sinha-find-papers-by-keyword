import pickle
import mysql.connector
import src.database.db_conn_factory as db_factory

def main():
    mag_db = db_factory.get_forward_db()

    id_file = "data/PaperIds.pickle"
    sql = "SELECT id FROM Publication"

    with mag_db.cursor() as cur, open(id_file, "wb") as out_file:
        cur.execute(sql)
        ids = cur.fetchall()
        ids = [i[0] for i in ids]

        pickle.dump(ids, out_file)


if __name__ == "__main__":
    main()