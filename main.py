from sqlalchemy import create_engine, text
import psycopg2

user = "postgres.beatuwbshkuodwcvdhfq"
host = "aws-0-us-west-1.pooler.supabase.com"
password = "My!Careers_21"
database = "postgres"
port = "6543"

connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

insert_statement = text("INSERT INTO students (first_name, last_name, school, password_hash, email) VALUES (:first_name, :last_name, :school, :password_hash, :email)").bindparams(
    first_name="Joshua",
    last_name="Udo",
    school="OHS",
    password_hash=1234,
    email="josh@josh.com"
)

engine = create_engine(connection_string)

with engine.connect() as connection:
  connection.execute(insert_statement)
  connection.commit()
  """result = connection.execute(
      text("select * from students WHERE email  = :email").bindparams(
          email="efgh"))
  results = result.mappings()
  if results:
    print(True)
  val = []
  for row in results:
    val.append(dict(row))

  #print(val[0]['first_name'])
  print(result[0])"""
