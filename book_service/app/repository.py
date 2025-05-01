# book_service/app/repository.py
from . import db
from .models import Book
from sqlalchemy import update # Güncelleme için import

class BookRepository:
    def add(self, book: Book) -> Book:
        db.session.add(book)
        # Commit service katmanında
        return book

    def get_by_id(self, book_id: int) -> Book | None:
        return db.session.get(Book, book_id) # SQLAlchemy 2.0+

    def get_by_isbn(self, isbn: str) -> Book | None:
        return Book.query.filter_by(isbn=isbn).first()

    def list_all(self, title: str | None = None, author: str | None = None) -> list[Book]:
        query = Book.query
        if title:
            # Basit title araması (case-insensitive)
            query = query.filter(Book.title.ilike(f"%{title}%"))
        if author:
            # Basit yazar araması (case-insensitive)
            query = query.filter(Book.author.ilike(f"%{author}%"))
        return query.order_by(Book.title).all()

    def update_book(self, book_id: int, data: dict) -> Book | None:
        # Sadece izin verilen alanları güncelle (güvenlik için)
        allowed_updates = {'title', 'author', 'quantity'}
        update_data = {k: v for k, v in data.items() if k in allowed_updates}

        if not update_data:
            # Güncellenecek bir şey yoksa veya izin verilmeyen alanlar varsa
            book = self.get_by_id(book_id)
            return book # Mevcut kitabı döndür veya None

        # Update işlemini yap
        stmt = update(Book).where(Book.book_id == book_id).values(**update_data)
        result = db.session.execute(stmt)

        if result.rowcount == 0:
            # Hiçbir satır güncellenmedi (kitap bulunamadı)
             return None

        # Güncellenen kitabı tekrar getir (veya commit sonrası session'dan al)
        # db.session.flush() # Değişiklikleri session'a yansıt
        # book = self.get_by_id(book_id)
        # return book
        # Şimdilik commit sonrası serviste tekrar get_by_id çağrılacağını varsayalım
        return True # Başarılı güncelleme olduğunu belirtelim (service tekrar getirecek)


    def increment_availability(self, book_id: int, amount: int = 1):
        """Ödünç verilebilir kitap sayısını artırır."""
        book = self.get_by_id(book_id)
        if book:
            # Toplam quantity'yi geçmemeli
            new_availability = min(book.available_quantity + amount, book.quantity)
            stmt = update(Book).where(Book.book_id == book_id).values(available_quantity=new_availability)
            db.session.execute(stmt)
            return True
        return False

    def decrement_availability(self, book_id: int, amount: int = 1):
        """Ödünç verilebilir kitap sayısını azaltır."""
        book = self.get_by_id(book_id)
        if book and book.available_quantity >= amount:
            new_availability = book.available_quantity - amount
            stmt = update(Book).where(Book.book_id == book_id).values(available_quantity=new_availability)
            db.session.execute(stmt)
            return True
        return False # Yeterli kitap yok veya kitap bulunamadı

    # Delete metodu eklenebilir (opsiyonel)
    # def delete(self, book_id: int) -> bool:
    #     book = self.get_by_id(book_id)
    #     if book:
    #         db.session.delete(book)
    #         return True
    #     return False