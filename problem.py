import psycopg2
import json
import sys


con = psycopg2.connect(database='test2', user='heyyyoyy', password='heyyyoyy')


def create_table():
    cur = con.cursor()
    sql = """CREATE TABLE IF NOT EXISTS organization (
                id INT, ParentId INT,
                Name VARCHAR (150), Type INT);"""
    cur.execute(sql)
    con.commit()
    cur.close()


def load_data():
    with open('data.json') as file:
        data = json.load(file)
    return data


def save_data(data):
    cur = con.cursor()
    sql = """INSERT INTO organization (
                id, ParentId, Name, type
                ) VALUES (%(id)s, %(ParentId)s, %(Name)s, %(Type)s);
    """
    cur.executemany(sql, data)
    con.commit()
    cur.close()


def get_office_id(cur, id):
    sql = 'SELECT * FROM organization WHERE id = %s;'
    cur.execute(sql, (id,))
    result = cur.fetchone()
    if result is not None:
        parent_id, type_ = result[1], result[3]
        if type_ != 1:
            return get_office_id(cur, parent_id)
        else:
            return result


def get_persons(cur, ids, persons=[]):
    sql = 'SELECT * FROM organization WHERE ParentId = %s;'
    for id in ids:
        cur.execute(sql, (id,))
        results = cur.fetchall()
        for res in results:
            id_, type_ = res[0], res[3]
            if type_ != 3:
                get_persons(cur, (id_,))
            else:
                persons.append(res)
    return (person[2] for person in persons)


cur = con.cursor()
person_id = input('Enter person id: ')
office = get_office_id(cur, int(person_id))

if office is None:
    print('Данный id не существует')
    sys.exit(1)

persons = get_persons(cur, [(office[0],)])
print(f'{office[2]}: {", ".join(persons)}')
cur.close()
con.close()
