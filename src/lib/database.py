import psycopg2


class DBConnectionManager:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Connected to database successfully!")

        except psycopg2.OperationalError as e:
            print(f"Error connecting to database: {e}")
            self.connection = None

    def is_connected(self):
        return self.connection is not None

    def close(self):
        if self.connection:
            self.connection.close()

    def commit(self):
        self.connection.commit()
    
    def rollback(self):
        self.connection.rollback()