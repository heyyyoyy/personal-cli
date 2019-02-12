import click
from .solution import DatabaseWorker
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(dotenv_path=Path('.') / '.env')

DB_NAME = os.environ['DB_NAME']
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


@click.group()
def cli():
    pass


@cli.command()
@click.argument('file_path')
def init_db(file_path):
    with DatabaseWorker(DB_NAME, user=DB_USER, password=DB_PASSWORD) as db:
        db.create_table()
        db.save_data(file_path)


@cli.command()
@click.argument('person_id')
def run(person_id):
    with DatabaseWorker(DB_NAME, user=DB_USER, password=DB_PASSWORD) as db:
        print(db.get_office_personal(int(person_id)))


if __name__ == "__main__":
    cli()
