# book_service/app/models.py
from . import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books' # RFC'deki tablo adı

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    # quantity: Kütüphanedeki toplam kopya sayısı
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # available_quantity: Şu anda rafta olan, ödünç verilebilir kopya sayısı
    available_quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

    # API yanıtları için
    def to_dict(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'quantity': self.quantity,
            'available_quantity': self.available_quantity,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }