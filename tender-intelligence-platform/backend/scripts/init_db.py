from sqlalchemy import create_engine

from app.config import get_settings
from app.database.models import Base


def main():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    print("Database initialized")


if __name__ == "__main__":
    main()
