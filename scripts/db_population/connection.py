from sqlalchemy import create_engine


engine = create_engine('postgresql://germanbulavkin:postgres@127.0.0.1:5432/postgres')

con = engine.connect()