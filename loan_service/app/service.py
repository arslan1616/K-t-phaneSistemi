# loan_service/app/service.py
import requests # HTTP istekleri için
from datetime import datetime
from flask import current_app # App context'inden config okumak için
from . import db
from .models import Loan
from .repository import LoanRepository

# Custom Exception sınıfları tanımlamak iyi bir pratik olabilir
class ServiceCommunicationError(Exception):
    """Diğer servislere erişimde hata olduğunu belirtir."""
    pass

class LoanLogicError(ValueError):
    """Ödünç alma/iade mantığıyla ilgili hatalar."""
    pass


class LoanService:
    def __init__(self):
        self.repository = LoanRepository()
        # Servis URL'lerini app context'inden al
        # Not: Bu __init__ içinde değil, metodlar içinde çağrılırken yapılmalı
        # çünkü app context'i o zaman aktif olur.

    def _get_service_url(self, service_name):
        """Helper to get service URL from config."""
        url = current_app.config.get(service_name)
        if not url:
            raise ServiceCommunicationError(f"{service_name} URL'si konfigürasyonda bulunamadı.")
        # URL'nin sonunda / olmamasını sağla
        return url.rstrip('/')

    def _check_user_exists(self, user_id: int) -> bool:
        """User Service'i çağırarak kullanıcı varlığını kontrol eder."""
        user_service_url = self._get_service_url('USER_SERVICE_URL')
        try:
            response = requests.get(f"{user_service_url}/users/validate/{user_id}", timeout=30) # Timeout eklemek önemli
            response.raise_for_status() # 4xx veya 5xx hataları için exception fırlatır
            # Yanıt 200 OK ise ve {"exists": true} ise kullanıcı vardır
            # Ancak /validate/ endpoint'i 404 döndüğünde de kullanıcı yoktur.
            # Status code yeterli.
            return response.status_code == 200
        except requests.exceptions.Timeout:
            raise ServiceCommunicationError(f"User Service'e ({user_service_url}) yapılan istek zaman aşımına uğradı.")
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response is not None else 'N/A'
            # 404 Not Found hatası kullanıcı olmadığını belirtir, bu bir hata değil.
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                 print(f"User Service kullanıcının olmadığını belirtti (ID: {user_id}).")
                 return False
            # Diğer hataları logla ve genel bir hata fırlat
            print(f"User Service ile iletişim hatası ({status_code}): {e}")
            raise ServiceCommunicationError(f"Kullanıcı servisi ile iletişim kurulamadı (Status: {status_code}).")

    def _check_book_availability(self, book_id: int) -> bool:
        """Book Service'i çağırarak kitabın varlığını ve ödünç alınabilirliğini kontrol eder."""
        book_service_url = self._get_service_url('BOOK_SERVICE_URL')
        try:
            response = requests.get(f"{book_service_url}/books/{book_id}/availability", timeout=5)
            response.raise_for_status() # 4xx, 5xx için hata
            data = response.json()
            return data.get('is_available', False)
        except requests.exceptions.Timeout:
            raise ServiceCommunicationError(f"Book Service'e ({book_service_url}) yapılan istek zaman aşımına uğradı.")
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response is not None else 'N/A'
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                 print(f"Book Service kitabın olmadığını belirtti (ID: {book_id}).")
                 return False # Kitap yoksa available değildir.
            print(f"Book Service ile iletişim hatası ({status_code}): {e}")
            raise ServiceCommunicationError(f"Kitap servisi ile iletişim kurulamadı (Status: {status_code}).")

    def _decrement_book_stock(self, book_id: int) -> bool:
        """Book Service'i çağırarak kitabın stoğunu azaltır."""
        book_service_url = self._get_service_url('BOOK_SERVICE_URL')
        try:
            response = requests.put(f"{book_service_url}/books/{book_id}/decrement", timeout=5)
            response.raise_for_status()
            # Başarılı ise 200 OK döner
            return response.status_code == 200
        except requests.exceptions.Timeout:
            raise ServiceCommunicationError(f"Book Service'e ({book_service_url}) stok azaltma isteği zaman aşımına uğradı.")
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response is not None else 'N/A'
            error_msg = f"Book Service stok azaltma hatası ({status_code}): {e}"
            if hasattr(e, 'response') and e.response is not None:
                 try:
                     error_details = e.response.json().get('error', str(e.response.text))
                     error_msg += f" - Details: {error_details}"
                 except requests.exceptions.JSONDecodeError:
                     error_msg += f" - Response: {e.response.text}"
            print(error_msg)
            # Eğer kitap bulunamadıysa (404) veya stok yetersizse (400) özel hata
            if status_code == 404:
                 raise LoanLogicError("Stok azaltılamadı: Kitap bulunamadı.")
            if status_code == 400:
                 raise LoanLogicError("Stok azaltılamadı: Kitap mevcut değil veya stok yetersiz.")
            # Diğer hatalar için genel iletişim hatası
            raise ServiceCommunicationError(f"Kitap servisine stok azaltma isteği gönderilemedi (Status: {status_code}).")


    def _increment_book_stock(self, book_id: int) -> bool:
        """Book Service'i çağırarak kitabın stoğunu artırır."""
        book_service_url = self._get_service_url('BOOK_SERVICE_URL')
        try:
            response = requests.put(f"{book_service_url}/books/{book_id}/increment", timeout=5)
            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.Timeout:
             raise ServiceCommunicationError(f"Book Service'e ({book_service_url}) stok artırma isteği zaman aşımına uğradı.")
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response is not None else 'N/A'
            print(f"Book Service stok artırma hatası ({status_code}): {e}")
            if status_code == 404:
                 # Bu durumda belki loglamak yeterli, iade işlemini durdurmayabiliriz?
                 # Veya hata fırlatabiliriz. Şimdilik hata fırlatalım.
                 raise LoanLogicError("Stok artırılamadı: Kitap bulunamadı.")
            raise ServiceCommunicationError(f"Kitap servisine stok artırma isteği gönderilemedi (Status: {status_code}).")


    def borrow_book(self, user_id: int, book_id: int):
        """Bir kitabı ödünç alma işlemini yönetir."""
        # 1. Kullanıcı var mı?
        if not self._check_user_exists(user_id):
            raise LoanLogicError(f"ID:{user_id} ile kullanıcı bulunamadı.")

        # 2. Kitap var mı ve ödünç alınabilir mi?
        if not self._check_book_availability(book_id):
            raise LoanLogicError(f"ID:{book_id} ile kitap bulunamadı veya mevcut değil.")

        # 3. Kullanıcı aynı kitabı zaten ödünç almış mı?
        if self.repository.find_active_loan(user_id, book_id):
            raise LoanLogicError(f"Kullanıcı (ID:{user_id}) zaten bu kitabı (ID:{book_id}) ödünç almış.")

        # --- İşlemi Başlat ---
        try:
            # 4. Kitap stoğunu azaltmayı dene
            stock_decremented = self._decrement_book_stock(book_id)

            if stock_decremented:
                # 5. Ödünç kaydı oluştur
                new_loan = Loan(user_id=user_id, book_id=book_id)
                added_loan = self.repository.add(new_loan)
                db.session.commit()
                print(f"Kitap (ID:{book_id}) kullanıcı (ID:{user_id}) tarafından ödünç alındı. Loan ID: {added_loan.loan_id}")
                # İleride bildirim servisine istek atılabilir
                return added_loan
            else:
                # Stok azaltılamadı (beklenmedik durum, _decrement_book_stock hata fırlatmalıydı)
                db.session.rollback() # Emin olmak için
                raise LoanLogicError("Kitap stoğu azaltılamadı (beklenmedik durum).")

        except (LoanLogicError, ServiceCommunicationError) as e:
             # Eğer stok azaltma veya diğer adımlarda hata olursa, işlemi geri al
             db.session.rollback()
             print(f"Ödünç alma hatası ({type(e).__name__}): {e}")
             # Eğer stok azaltma başarılı olduysa ama sonra hata alındıysa, stoğu geri artırmak gerekir mi?
             # Bu senaryo yönetimi (Saga Pattern vb.) daha karmaşıktır. Şimdilik basit tutalım.
             # Eğer decrement hata fırlattıysa zaten commit olmaz.
             raise e # Hatayı yukarıya tekrar fırlat
        except Exception as e:
             db.session.rollback()
             print(f"Ödünç alma sırasında beklenmedik genel hata: {e}")
             raise RuntimeError("Ödünç alma işlemi sırasında bir sunucu hatası oluştu.")

    def return_book(self, loan_id: int):
        """Bir kitabın iade işlemini yönetir."""
        loan = self.repository.get_by_id(loan_id)

        if not loan:
            raise LoanLogicError(f"ID:{loan_id} ile ödünç kaydı bulunamadı.")
        if loan.return_date is not None:
            raise LoanLogicError(f"Bu ödünç kaydı (ID:{loan_id}) zaten iade edilmiş.")

        # --- İşlemi Başlat ---
        try:
            # 1. Kitap stoğunu artırmayı dene
            stock_incremented = self._increment_book_stock(loan.book_id)

            if stock_incremented:
                # 2. Ödünç kaydını güncelle (iade edildi olarak işaretle)
                return_time = datetime.utcnow()
                status = 'returned'
                updated = self.repository.update_loan_status(loan_id, return_time, status)
                if updated:
                    db.session.commit()
                    print(f"Ödünç kaydı (ID:{loan_id}) başarıyla iade edildi.")
                    # İleride bildirim servisine istek atılabilir
                    # Güncellenmiş loan objesini döndürmek için tekrar getirelim
                    return self.repository.get_by_id(loan_id)
                else:
                    # Bu durum olmamalı ama olursa diye...
                    db.session.rollback()
                    raise RuntimeError("Ödünç kaydı durumu güncellenemedi.")
            else:
                 # Stok artırılamadı (beklenmedik durum, _increment_book_stock hata fırlatmalıydı)
                 db.session.rollback()
                 raise LoanLogicError("Kitap stoğu artırılamadı (beklenmedik durum).")

        except (LoanLogicError, ServiceCommunicationError) as e:
             db.session.rollback()
             print(f"İade işlemi hatası ({type(e).__name__}): {e}")
             # Stok artırıldı ama loan güncellenemezse ne olacak? Compensation gerekebilir.
             # Şimdilik basit tutuyoruz.
             raise e
        except Exception as e:
             db.session.rollback()
             print(f"İade işlemi sırasında beklenmedik genel hata: {e}")
             raise RuntimeError("İade işlemi sırasında bir sunucu hatası oluştu.")

    def get_loans_by_user(self, user_id):
        # Kullanıcının varlığını kontrol etmeye gerek var mı? Varsa User Service çağrılabilir.
        # Şimdilik sadece loan kayıtlarını döndürelim.
        return self.repository.list_by_user(user_id)

    def get_loans_by_book(self, book_id):
        # Kitabın varlığını kontrol etmeye gerek var mı?
        return self.repository.list_by_book(book_id)

    def get_overdue_loans(self):
        return self.repository.list_overdue()