Установка и запуск (``requirements.txt``)
=========================================

Подготовка
----------

    Клонируем репозиторий

    .. code-block:: bash

        $ git clone https://github.com/heyyyoyy/personal-cli.git
        $ cd personal-cli

    Создаем и активируем виртуальное окружение для работы

    .. code-block:: bash

        $ python3.7 -m venv venv
        $ source venv/bin/activate


Установка зависимостей
--------------------------------

    .. code-block:: bash

        (venv)$ pip install -r requirements.txt


Загрузка данных в базу
----------------------

    .. code-block:: bash

        (venv)$ python -m personal_cli init-db
    
Пример использования
--------------------

    .. code-block:: bash

        (venv)$ python -m personal_cli run 4
        Офис в Санкт-Петербурге: Иванов, Сидоров, Петров

