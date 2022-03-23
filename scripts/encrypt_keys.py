# import sys
# import os
# import psycopg2
# import boto3
# from app.src.config.parameter_store import RelationalDB
#
# a = boto3.client("ssm")
# kms_client = boto3.client("kms")
#
#
# def main(args):
#     env = os.environ.get("PLANET_ENV", "dev")
#
#     select_query = """SELECT id, private_key FROM users"""
#
#     conn = psycopg2.connect(dbname=RelationalDB.name(),
#                             user=RelationalDB.user(),
#                             password=RelationalDB.password(),
#                             host=RelationalDB.host())
#
#     print(f"Connecting to DB: {RelationalDB.host()}")
#
#     cursor = conn.cursor()
#
#     cursor.execute(select_query)
#     records = cursor.fetchall()
#
#
# # Ideally would be run "python ./migrate_between_buckets_from_table.py SRC_BUCKET DEST_BUCKET"
# if __name__ == "__main__":
#     main(sys.argv)
