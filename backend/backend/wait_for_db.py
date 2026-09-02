import sys
import time
from sqlalchemy import create_engine
from app.config import settings

def wait_for_db():
    print(f'Checking database: {settings.database_url}')
    engine = create_engine(settings.database_url)
    for i in range(15):
        try:
            with engine.connect() as conn:
                print('Database is ready!')
                sys.exit(0)
        except Exception as e:
            print(f'Waiting for database... {i+1}/15')
            time.sleep(2)
    print('Database not ready after 30 seconds.')
    sys.exit(1)

if __name__ == '__main__':
    wait_for_db()
