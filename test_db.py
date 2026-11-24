import pymysql

connection = None

try:
    connection = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Srini@18",
        database="fake_profile_detection"
    )

    print("SUCCESS: Connected to MySQL!")
    print("Database: fake_profile_detection")

    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE()")
        print("Current database:", cursor.fetchone()[0])

except pymysql.MySQLError as error:
    print("Database connection failed:", error)

finally:
    if connection is not None:
        connection.close()