# loan_service/app/models.py
from . import db
from datetime import datetime, timedelta

class Loan(db.Model):
    __tablename__ = 'loans'

    loan_id = db.Column(db.Integer, primary_key=True)
    # Foreign Key'ler normalde tanımlanır ama mikroservislerde ID'leri tutmak yeterli
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Ödünç süresi (örn: 14 gün)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True) # Kitap iade edildiğinde dolar
    # status: 'active', 'returned', 'overdue'
    status = db.Column(db.String(20), nullable=False, default='active')

    def __init__(self, user_id, book_id, loan_period_days=14, **kwargs):
        super().__init__(user_id=user_id, book_id=book_id, **kwargs)
        self.loan_date = kwargs.get('loan_date', datetime.utcnow())
        self.due_date = self.loan_date + timedelta(days=loan_period_days)
        self.status = 'active' # Başlangıç durumu

    def __repr__(self):
        return f'<Loan {self.loan_id} - User: {self.user_id}, Book: {self.book_id}>'

    def to_dict(self):
        # Durumu kontrol et (iade tarihi geçtiyse ve dönmediyse 'overdue' yap)
        current_status = self.status
        if self.status == 'active' and datetime.utcnow() > self.due_date:
            current_status = 'overdue'

        return {
            'loan_id': self.loan_id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'loan_date': self.loan_date.isoformat() if self.loan_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': current_status
        }