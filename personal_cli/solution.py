import psycopg2
import json


class DatabaseWorker:
    def __init__(self, database, user=None, password=None):
        """
        Класс для работы с базой данных. Пример использования::

            with Database(database='test', user='user', password='pass') as db:
               db.create_table()

        :param database: Имя базы данных
        :type database: :obj:`str`
        :param user: Имя пользователя базы данных
        :type user: :obj:`Options[str]`
        :param password: Пароль пользователя от базы данных
        :type password: :obj:`Options[str]`
        :return: :obj:`None`
        """
        self.database = database
        self.user = user
        self.password = password

    def create_table(self):
        """
        Создание таблицы и индексов
        """
        cur = self.conn.cursor()
        sql = """CREATE TABLE IF NOT EXISTS organization (
                    id INT, ParentId INT,
                    Name VARCHAR (150), Type INT);
                CREATE INDEX
                IF NOT EXISTS organization_id_idx
                on organization (id);
                CREATE INDEX
                IF NOT EXISTS organization_parentid_idx
                on organization (parentid);
                """
        cur.execute(sql)
        self.conn.commit()
        cur.close()

    def load_data(self, path):
        """
        Загрузка данных из файла

        :param path: Путь до файла в формате `json`
        :type path: :obj:`str`
        :return: Словарь с данными пользователей
        :rtype: :obj:`dict`
        """
        with open(path) as file:
            data = json.load(file)
        return data

    def save_data(self, path):
        """
        Сохранение данных в таблице

        :param path: Путь до файла в формате `json`
        :type path: :obj:`str`
        :return: :obj:`None`
        """
        data = self.load_data(path)
        cur = self.conn.cursor()
        sql = """INSERT INTO organization (
                    id, ParentId, Name, type
                    ) VALUES (%(id)s, %(ParentId)s, %(Name)s, %(Type)s);
        """
        cur.executemany(sql, data)
        self.conn.commit()
        cur.close()

    def __enter__(self):
        """
        Возвращает подключение к базе данных

        :return: Подключение к базе данных
        :rtype: :class:`psycopg2.extensions.connection`
        """
        self.conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def get_office_id_sql(self, cur, id):
        """
        Возвращает идентификатор офиса по указаному идентификатору сотрудника

        Используется рекурсивный запрос sql

        :param cur: Курсор
        :type cur: :class:`psycopg2.extensions.cursor`
        :param id: Идентификатор сотрудника
        :type id: :obj:`int`
        :return: Результат запроса
        :rtype: :obj:`Options[tuple]`
        """
        sql = """with recursive r as (
                    select id,parentid,name,type from organization
                    where id = %s
                    union
                    select org.id,org.parentid,org.name,org.type
                    from organization org
                    join r on org.id = r.parentid
                )
                select * from r where type = 1;"""
        cur.execute(sql, (id,))
        result = cur.fetchone()
        if result is not None:
            return result

    def get_persons_sql(self, cur, office_id):
        """
        Возвращает массив сотрудников, работающих в данном офисе

        Используется рекурсивный запрос sql

        :param cur: Курсор
        :type cur: :class:`psycopg2.extensions.cursor`
        :param office_id: Идентификатор офиса
        :type office_id: :obj:`int`
        :return: Массив с именами сотрудников
        :rtype: :obj:`list`
        """
        sql = """with recursive r as(
                    select id,parentid,name,type
                    from organization
                    where id=%s
                    union
                    select org.id, org.parentid, org.name,org.type
                    from organization org
                    join r on org.parentid = r.id
                )
                select * from r where type=3;"""
        cur.execute(sql, (office_id,))
        results = cur.fetchall()
        return [person[2] for person in results]

    def get_office_id(self, cur, id):
        """
        Возвращает идентификатор офиса по указаному идентификатору сотрудника

        Используется обход таблицы средствами python

        :param cur: Курсор
        :type cur: :class:`psycopg2.extensions.cursor`
        :param id: Идентификатор сотрудника
        :type id: :obj:`int`
        :return: Результат запроса
        :rtype: :obj:`Options[tuple]`
        """
        sql = 'SELECT * FROM organization WHERE id = %s;'
        cur.execute(sql, (id,))
        result = cur.fetchone()
        if result is not None:
            parent_id, type_ = result[1], result[3]
            if type_ != 1:
                return self.get_office_id(cur, parent_id)
            else:
                return result

    def get_persons(self, cur, ids, persons=[]):
        """
        Возвращает массив сотрудников, работающих в данном офисе

        Используется обход таблицы средствами python

        :param cur: Курсор
        :type cur: :class:`psycopg2.extensions.cursor`
        :param ids: Список идентификаторов
        :type ids: :obj:`list`
        :param persons: Список сотрудников в офисе
        :type persons: :obj:`list`
        :return: Массив сотрудников
        :rtype: :obj:`list`
        """
        sql = 'SELECT * FROM organization WHERE ParentId = %s;'
        for id in ids:
            cur.execute(sql, (id,))
            results = cur.fetchall()
            for res in results:
                id_, type_ = res[0], res[3]
                if type_ != 3:
                    self.get_persons(cur, (id_,))
                else:
                    persons.append(res)
        return [person[2] for person in persons]

    def get_office_personal(self, person_id):
        """
        Метод получает на вход идентификатор сотрудника, возвращает строковое
        представление сотрудников работающих в офисе или, если идентификатора
        не существует в базе, строку с описание проблемы

        :param person_id: Идентификатор сотрудника
        :type person_id: :obj:`int`
        :return: Строка с описанием
        :rtype: :obj:`str`
        """
        cur = self.conn.cursor()
        office = self.get_office_id_sql(cur, person_id)
        if office is None:
            return 'Данный id не существует'

        persons = self.get_persons_sql(cur, office[0])
        cur.close()
        return f'{office[2]}: {", ".join(persons)}'
