Текущее решение
===============

Текущее рещение реализовано двумя способами:

1. Рекурсивный обхода таблицы с помощью python :obj:`personal_cli.solution.DatabaseWorker.get_office_id`

    .. code-block:: python3

        def get_office_id(self, cur, id):
            sql = 'SELECT * FROM organization WHERE id = %s;'
            cur.execute(sql, (id,))
            result = cur.fetchone()
            if result is not None:
                parent_id, type_ = result[1], result[3]
                if type_ != 1:
                    return self.get_office_id(cur, parent_id)
                else:
                    return result

2. Рекурсивный обход средсвами sql :obj:`personal_cli.solution.DatabaseWorker.get_office_id_sql`

    .. code-block:: python3

        def get_office_id_sql(self, cur, id):
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
