# book_service/app/api.py
from flask import Blueprint, request, jsonify
from .service import BookService
from . import db

bp = Blueprint('api', __name__)
book_service = BookService() # Basit DI

@bp.route('', methods=['POST']) # /books adresine POST
def add_book():
    data = request.get_json()
    if not data or not 'title' in data or not 'author' in data or not 'isbn' in data:
        return jsonify({"error": "Eksik bilgi: title, author ve isbn gereklidir."}), 400

    title = data['title']
    author = data['author']
    isbn = data['isbn']
    # quantity opsiyonel, varsayılanı 1 service katmanında ayarlı
    quantity = data.get('quantity', 1)

    try:
        # Adet integer olmalı
        quantity = int(quantity)
        new_book = book_service.add_new_book(title, author, isbn, quantity)
        return jsonify(new_book.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Bilinmeyen hata (add_book): {e}")
        db.session.rollback()
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500

@bp.route('', methods=['GET']) # /books adresine GET
def list_books():
    # Arama parametreleri (opsiyonel)
    title = request.args.get('title')
    author = request.args.get('author')

    try:
        books = book_service.search_books(title=title, author=author)
        return jsonify([book.to_dict() for book in books]), 200
    except Exception as e:
        print(f"Bilinmeyen hata (list_books): {e}")
        return jsonify({"error": "Kitaplar listelenirken bir hata oluştu."}), 500

@bp.route('/<int:book_id>', methods=['GET']) # /books/1 gibi GET
def get_book(book_id):
    try:
        book = book_service.get_book_details(book_id)
        return jsonify(book.to_dict()), 200
    except ValueError as e: # Kitap bulunamadı hatası
        return jsonify({"error": str(e)}), 404 # Not Found
    except Exception as e:
        print(f"Bilinmeyen hata (get_book): {e}")
        return jsonify({"error": "Kitap detayı alınırken bir hata oluştu."}), 500

@bp.route('/<int:book_id>', methods=['PUT']) # /books/1 gibi PUT
def update_book(book_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Güncelleme verisi gönderilmedi."}), 400

    try:
        updated_book = book_service.update_book_details(book_id, data)
        if updated_book:
             return jsonify(updated_book.to_dict()), 200
        else:
             # Service None döndürdüyse (örn. bulunamadı), ama hata fırlatmadıysa
             return jsonify({"error": f"ID:{book_id} ile kitap bulunamadı veya güncelleme yapılamadı."}), 404
    except ValueError as e: # Kitap bulunamadı veya geçersiz veri
        return jsonify({"error": str(e)}), 400 # Veya 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Bilinmeyen hata (update_book): {e}")
        db.session.rollback()
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500


# --- Loan Service tarafından kullanılacak Endpointler ---

@bp.route('/<int:book_id>/availability', methods=['GET'])
def get_availability(book_id):
    """Bir kitabın ödünç alınabilir olup olmadığını kontrol eder."""
    try:
        is_available = book_service.check_availability(book_id)
        return jsonify({"book_id": book_id, "is_available": is_available}), 200
    except Exception as e:
        print(f"Bilinmeyen hata (get_availability): {e}")
        # Loan service'e uygun bir hata dönmek önemli
        return jsonify({"error": "Kitap durumu kontrol edilirken bir hata oluştu."}), 500


@bp.route('/<int:book_id>/decrement', methods=['PUT'])
def decrement_stock(book_id):
    """Kitap ödünç verildiğinde stoğu azaltır (Loan Service çağırır)."""
    try:
        success = book_service.decrease_book_stock(book_id)
        if success:
            return jsonify({"message": "Stok başarıyla azaltıldı."}), 200
        else:
            # Kitap bulunamadı veya stok yetersiz
            return jsonify({"error": "Stok azaltılamadı (kitap yok veya mevcut değil)."}), 400 # Veya 404
    except RuntimeError as e: # Servisten gelen özel hata
         return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Bilinmeyen hata (decrement_stock): {e}")
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500

@bp.route('/<int:book_id>/increment', methods=['PUT'])
def increment_stock(book_id):
    """Kitap iade edildiğinde stoğu artırır (Loan Service çağırır)."""
    try:
        success = book_service.increase_book_stock(book_id)
        if success:
            return jsonify({"message": "Stok başarıyla artırıldı."}), 200
        else:
            # Kitap bulunamadı
            return jsonify({"error": "Stok artırılamadı (kitap bulunamadı)."}), 404
    except RuntimeError as e: # Servisten gelen özel hata
         return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Bilinmeyen hata (increment_stock): {e}")
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500