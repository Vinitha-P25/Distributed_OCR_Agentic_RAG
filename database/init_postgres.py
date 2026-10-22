from database.postgres_db import Base, engine
from database.postgres_models import Document


def initialize_database():
    try:
        Base.metadata.create_all(bind=engine)

        print("PostgreSQL connection successful.")
        print("Documents table created or already exists.")

    except Exception as error:
        print(f"Database initialization failed: {error}")
        raise


if __name__ == "__main__":
    initialize_database()