from psycopg2 import connect as pg_connect
from mysql.connector import connect as my_sql_connect


config_dict = {'dbname': 'postgres', 'user': 'user', 'password': 'pass', 'host': 'localhost'}
conn_ = pg_connect

# config_dict = {'database': 'db', 'user': 'root', 'password': 'pass', 'host': 'localhost'}
# conn_ = my_sql_connect

conn_1 = conn_(**config_dict)
conn_2 = conn_(**config_dict)


def initial_db():
    conn = conn_(**config_dict)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS users;')
    conn.commit()
    cursor.execute('CREATE table users ('
                   'name varchar(80),'
                   'second_name varchar(80),'
                   'money  integer)')
    cursor.execute("INSERT INTO users  (name, second_name, money) VALUES (%s, %s, %s);", ('Vasya', 'Petrov', 100))
    conn.commit()
    conn.close()


cursor_1 = conn_1.cursor()
cursor_2 = conn_2.cursor()


# ---------------LOST UPDATE--------------
initial_db()
cursor_1.execute('select sum(money),count(*) from users;')
initial_sum, initial_count = cursor_1.fetchone()


cursor_2.execute("update users set money=money+300;")


cursor_1.execute("update users set money=money+400;")
conn_2.commit()

conn_1.commit()


cursor_1.execute('select sum(money),count(*) from users;')
second_sum, second_count = cursor_1.fetchone()

print('LOST UPDATE (changes overridden)')
print(f'initial: sum:{initial_sum}, count:{initial_count}')
print(f'changed: sum: {second_sum}, count: {second_count}')
print(f'should be : sum:800 , count: {initial_count}')
print(f'error: {second_sum!=800 or second_count!= initial_count}\n')

conn_2.commit()
conn_1.commit()



# ---------------PHANTOM READ------------
initial_db()
cursor_1.execute('select sum(money),count(*) from users;')
initial_sum, initial_count = cursor_1.fetchone()
cursor_2.execute('INSERT INTO users (name, second_name, money) VALUES (%s, %s, %s)', ('Petya', 'Petrov', 200))
conn_2.commit()

cursor_1.execute('select sum(money),count(*) from users;')
second_sum, second_count = cursor_1.fetchone()

print('PHANTOM READ (new entries)')
print(f'initial: sum:{initial_sum}, count:{initial_count}')
print(f'new: sum:{second_sum}, count:{second_count}')
print(f'changed: sum: {second_sum!=initial_sum}, count: {second_count!=initial_count}')
print(f'error: {second_sum!=initial_sum or second_count!= initial_count}\n')




conn_2.commit()
conn_1.commit()

# --------------UNREPEATABLE READ--------------
initial_db()
cursor_1.execute('select sum(money),count(*) from users;')
initial_sum, initial_count = cursor_1.fetchone()

cursor_2.execute("update users set money=money+300;")
conn_2.commit()


cursor_1.execute('select sum(money),count(*) from users;')
second_sum, second_count = cursor_1.fetchone()

print('UNREPEATABLE REA (changed entries)')
print(f'initial: sum:{initial_sum}, count:{initial_count}')
print(f'new: sum:{second_sum}, count:{second_count}')
print(f'changed: sum: {second_sum!=initial_sum}, count: {second_count!=initial_count}')
print(f'error: {second_sum!=initial_sum or second_count!= initial_count}\n')

conn_2.commit()
conn_1.commit()
# --------------DIRTY READ--------------
initial_db()
cursor_1.execute('select sum(money),count(*) from users;')
initial_sum, initial_count = cursor_1.fetchone()

cursor_2.execute("update users set money=money+300;")
cursor_1.execute('select sum(money),count(*) from users;')
second_sum, second_count = cursor_1.fetchone()
conn_2.rollback()

print('DIRTY READ (rolled back changes)')
print(f'initial: sum:{initial_sum}, count:{initial_count}')
print(f'new: sum:{second_sum}, count:{second_count}')
print(f'changed: sum: {second_sum!=initial_sum}, count: {second_count!=initial_count}')
print(f'error: {second_sum!=initial_sum or second_count!= initial_count}\n')

conn_2.commit()
conn_1.commit()


conn_2.close()
conn_1.close()






