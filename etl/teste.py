from database.models import init_db

engine = init_db()

conexao = engine.raw_connection()
cursor = conexao.cursor()

print("Tipo da conexão:", type(conexao))
print("Tipo do cursor:", type(cursor))
print("Driver SQLAlchemy:", engine.dialect.driver)

cursor.close()
conexao.close()