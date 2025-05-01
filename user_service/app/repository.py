# user_service/app/repository.py
from . import db
from .models import User
# İleride soyutlama (ABC) eklenebilir (OCP/DIP için)

class UserRepository:
    def add(self, user: User):
        db.session.add(user)
        # db.session.commit() # Commit işlemini service katmanında yapmak daha iyi olabilir
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return db.session.get(User, user_id) # SQLAlchemy 2.0+

    def get_by_username(self, username: str) -> User | None:
        return User.query.filter_by(username=username).first()

    def get_by_email(self, email: str) -> User | None:
        return User.query.filter_by(email=email).first()

    def list_all(self) -> list[User]:  # <-- YENİ METOD
        return User.query.order_by(User.username).all()
    # Diğer CRUD operasyonları (update, delete, list) buraya eklenebilir