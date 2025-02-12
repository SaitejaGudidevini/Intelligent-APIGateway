from app.core.database import Base, engine
from app.models.user import User


print("Creating database tables ..")
Base.metadata.create_all(bind=engine)
print("Database tables Created successfully")