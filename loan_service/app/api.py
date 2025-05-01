# loan_service/app/api.py
from flask import Blueprint, request, jsonify
from .service import LoanService, LoanLogicError, ServiceCommunicationError
from . import db # Rollback için

bp = Blueprint('api', __name__)
loan_service = LoanService() # Basit DI

@bp.route('', methods=['POST']) # /loans
def borrow_book_api():
    data = request.get_json()
    if not data or 'user_id' not in data or 'book_id' not in data:
        return jsonify({"error": "Eksik bilgi: user_id ve book_id gereklidir."}), 400

    try:
        user_id = int(data['user_id'])
        book_id = int(data['book_id'])
        new_loan = loan_service.borrow_book(user_id, book_id)
        return jsonify(new_loan.to_dict()), 201 # Created

    except (LoanLogicError, ValueError) as e: # Beklenen mantık/veri hataları
        return jsonify({"error": str(e)}), 400 # Bad Request
    except ServiceCommunicationError as e: # Diğer servislerle iletişim hatası
        # Bu durumda 503 Service Unavailable veya 502 Bad Gateway daha uygun olabilir
        return jsonify({"error": str(e)}), 503
    except RuntimeError as e: # Beklenmeyen iç hata (service'den)
        return jsonify({"error": str(e)}), 500
    except Exception as e: # Diğer tüm hatalar
        print(f"Bilinmeyen hata (borrow_book_api): {e}")
        # db.session.rollback() # Service katmanı zaten yapmalı ama emin olmak için
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500

@bp.route('/<int:loan_id>/return', methods=['PUT']) # /loans/1/return
def return_book_api(loan_id):
    try:
        updated_loan = loan_service.return_book(loan_id)
        return jsonify(updated_loan.to_dict()), 200 # OK

    except LoanLogicError as e: # Ödünç kaydı yok, zaten iade edilmiş vb.
        # Duruma göre 404 veya 400 olabilir. Şimdilik 400 kullanalım.
        status_code = 404 if "bulunamadı" in str(e) else 400
        return jsonify({"error": str(e)}), status_code
    except ServiceCommunicationError as e: # Kitap stoğu artırılamadı vb.
        return jsonify({"error": str(e)}), 503
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Bilinmeyen hata (return_book_api): {e}")
        return jsonify({"error": "Beklenmeyen bir sunucu hatası oluştu."}), 500

@bp.route('/user/<int:user_id>', methods=['GET']) # /loans/user/1
def get_user_loans(user_id):
    try:
        loans = loan_service.get_loans_by_user(user_id)
        return jsonify([loan.to_dict() for loan in loans]), 200
    except Exception as e:
        print(f"Bilinmeyen hata (get_user_loans): {e}")
        return jsonify({"error": "Kullanıcı ödünçleri listelenirken bir hata oluştu."}), 500

@bp.route('/book/<int:book_id>', methods=['GET']) # /loans/book/1
def get_book_loans(book_id):
    try:
        loans = loan_service.get_loans_by_book(book_id)
        return jsonify([loan.to_dict() for loan in loans]), 200
    except Exception as e:
        print(f"Bilinmeyen hata (get_book_loans): {e}")
        return jsonify({"error": "Kitap ödünçleri listelenirken bir hata oluştu."}), 500

@bp.route('/overdue', methods=['GET']) # /loans/overdue
def get_overdue():
    # Bu endpoint ileride Notification Service tarafından kullanılabilir
    try:
        overdue_loans = loan_service.get_overdue_loans()
        return jsonify([loan.to_dict() for loan in overdue_loans]), 200
    except Exception as e:
        print(f"Bilinmeyen hata (get_overdue): {e}")
        return jsonify({"error": "Gecikmiş ödünçler listelenirken bir hata oluştu."}), 500