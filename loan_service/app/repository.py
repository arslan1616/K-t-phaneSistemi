# loan_service/app/repository.py
from . import db
from .models import Loan
from sqlalchemy import update, or_ # or_ koşulu için
from datetime import datetime

class LoanRepository:
    def add(self, loan: Loan) -> Loan:
        db.session.add(loan)
        return loan

    def get_by_id(self, loan_id: int) -> Loan | None:
        return db.session.get(Loan, loan_id)

    def list_by_user(self, user_id: int, only_active: bool = False) -> list[Loan]:
        query = Loan.query.filter_by(user_id=user_id)
        if only_active:
            # Henüz iade edilmemişleri getir (active veya overdue)
            query = query.filter(Loan.return_date.is_(None))
        return query.order_by(Loan.loan_date.desc()).all()

    def list_by_book(self, book_id: int, only_active: bool = False) -> list[Loan]:
        query = Loan.query.filter_by(book_id=book_id)
        if only_active:
            query = query.filter(Loan.return_date.is_(None))
        return query.order_by(Loan.loan_date.desc()).all()

    def find_active_loan(self, user_id: int, book_id: int) -> Loan | None:
        """Bir kullanıcının belirli bir kitabı aktif olarak ödünç alıp almadığını bulur."""
        return Loan.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            return_date=None # Henüz iade edilmemiş
        ).first()

    def list_overdue(self) -> list[Loan]:
        """İade tarihi geçmiş ve henüz iade edilmemiş tüm ödünçleri listeler."""
        return Loan.query.filter(
            Loan.due_date < datetime.utcnow(),
            Loan.return_date.is_(None) # Henüz iade edilmemiş
        ).order_by(Loan.due_date).all()

    def update_loan_status(self, loan_id: int, return_date: datetime, status: str) -> bool:
        """Ödünç kaydının iade tarihini ve durumunu günceller."""
        stmt = update(Loan).where(Loan.loan_id == loan_id).values(
            return_date=return_date,
            status=status
        )
        result = db.session.execute(stmt)
        return result.rowcount > 0 # Güncelleme başarılıysa True döner