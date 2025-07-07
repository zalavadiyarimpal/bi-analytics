from django.conf import settings
from sqlalchemy import create_engine, MetaData

def get_engine_select(db_connector_id:str):
    db = settings.DATABASES['default']
    
    db_user = db['USER']
    db_password = db['PASSWORD']
    db_host = db['HOST'] or 'localhost'
    db_port = db['PORT'] or '3306'
    db_name = db['NAME']

    # Build SQLAlchemy URL
    db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)

def reflect_tables(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return metadata

def get_engine_create():
    db = settings.DATABASES['create']
    
    db_user = db['USER']
    db_password = db['PASSWORD']
    db_host = db['HOST'] or 'localhost'
    db_port = db['PORT'] or '3306'
    db_name = db['NAME']

    # Build SQLAlchemy URL
    db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)
