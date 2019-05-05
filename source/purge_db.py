
import mysql.connector
import shutil
import os.path
import crossparser_tools


credentials = crossparser_tools.parse_credentials()
temp_folder = crossparser_tools.temp_folder
config_folder = crossparser_tools.config_folder

sql_query = ''


def parse_sql_query():
    global sql_query
    with open(config_folder + 'sql_truncate.txt', 'r') as cr_file:
        for line in cr_file:
            line = line.split(' ')
            line[1] = credentials['php_db'] + '.' + line[1]
            line = (' ').join(line)
            sql_query += line + '\n'

        sql_query = sql_query.replace('\n\n', '\n')


def clear_db():

    global sql_query
    parse_sql_query()
    #print(sql_query)

    mydb = mysql.connector.connect(
      host='localhost',
      user=credentials['php_login'],
      passwd=credentials['php_password'],
      database=credentials['php_db']
    )

    mycursor = mydb.cursor()

    sql_queries = sql_query.split('\n')
    for query in sql_queries:
        mycursor.execute(query)
    #sql_query = 'TRUNCATE bootsmarketdb.`oc_product_to_category`;'
    #mycursor.execute(sql_query, multi=True)

    sql_query = 'SELECT * FROM bootsmarketdb.`oc_product_option_value`;'
    mycursor.execute(sql_query)

    myresult = mycursor.fetchall()
    #print(myresult)

    if len(myresult) == 0 :
            crossparser_tools.write_to_log('db successfully purged')
    else:
        crossparser_tools.write_to_log('db purge failed')



clear_db()
