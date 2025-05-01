# book_service/app/service.py
from . import db
from .models import Book
from .repository import BookRepository

class BookService:
    def __init__(self):
        # DIP için: IBookRepository inject edilmeli
        self.repository = BookRepository()

    def add_new_book(self, title, author, isbn, quantity=1):
        if quantity < 1:
            raise ValueError("Kitap adedi en az 1 olmalıdır.")
        if self.repository.get_by_isbn(isbn):
            raise ValueError(f"ISBN: {isbn} ile kayıtlı bir kitap zaten var.")

        # Yeni kitap oluştururken available_quantity de quantity kadar olmalı
        new_book = Book(
            title=title,
            author=author,
            isbn=isbn,
            quantity=quantity,
            available_quantity=quantity # Başlangıçta hepsi mevcut
        )
        try:
            added_book = self.repository.add(new_book)
            db.session.commit()
            return added_book
        except Exception as e:
            db.session.rollback()
            print(f"Kitap eklenirken hata: {e}")
            raise RuntimeError("Kitap eklenirken bir sunucu hatası oluştu.")

    def get_book_details(self, book_id):
        book = self.repository.get_by_id(book_id)
        if not book:
            raise ValueError(f"ID:{book_id} ile kitap bulunamadı.") # NotFoundError
        return book

    def search_books(self, title=None, author=None):
        return self.repository.list_all(title=title, author=author)

    def update_book_details(self, book_id, data):
        # Önce kitabın varlığını kontrol et
        book = self.repository.get_by_id(book_id)
        if not book:
            raise ValueError(f"ID:{book_id} ile kitap bulunamadı.") # NotFoundError

        # Adet güncelleniyorsa, ödünç verilebilir adedi de ayarla
        if 'quantity' in data:
            new_quantity = data['quantity']
            if new_quantity < book.quantity - book.available_quantity:
                 raise ValueError("Toplam adet, ödünçteki kitap sayısından az olamaz.")
            # Yeni adet ile eski ödünçteki kitap sayısı farkı kadar available quantity olur
            data['available_quantity'] = new_quantity - (book.quantity - book.available_quantity)

        try:
            updated = self.repository.update_book(book_id, data)
            if updated:
                db.session.commit()
                # Güncellenmiş veriyi döndür
                return self.repository.get_by_id(book_id)
            else:
                 # Güncelleme yapılamadı (belki de data boştu veya kitap yoktu)
                 return book # Mevcut halini döndür
        except Exception as e:
            db.session.rollback()
            print(f"Kitap güncellenirken hata: {e}")
            raise RuntimeError("Kitap güncellenirken bir sunucu hatası oluştu.")


    def check_availability(self, book_id):
        """Kitabın ödünç alınıp alınamayacağını kontrol eder."""
        book = self.repository.get_by_id(book_id)
        return book and book.available_quantity > 0

    def decrease_book_stock(self, book_id):
        """Kitap ödünç verildiğinde stoğu azaltır."""
        try:
            decreased = self.repository.decrement_availability(book_id)
            if decreased:
                db.session.commit()
                return True
            else:
                # Stok azaltılamadı (kitap yok veya stok 0)
                db.session.rollback() # Emin olmak için
                return False
        except Exception as e:
            db.session.rollback()
            print(f"Kitap stoğu azaltılırken hata: {e}")
            # Bu hata Loan Service'e bildirilmeli
            raise RuntimeError("Stok azaltılırken bir sunucu hatası oluştu.")

    def increase_book_stock(self, book_id):
        """Kitap iade edildiğinde stoğu artırır."""
        try:
            increased = self.repository.increment_availability(book_id)
            if increased:
                db.session.commit()
                return True
            else:
                # Stok artırılamadı (kitap yok)
                db.session.rollback()
                return False
        except Exception as e:
            db.session.rollback()
            print(f"Kitap stoğu artırılırken hata: {e}")
            # Bu hata Loan Service'e bildirilmeli
            raise RuntimeError("Stok artırılırken bir sunucu hatası oluştu.")