// script.js

// API Base URL'leri (Aynı kalır)
const USER_SERVICE_URL = 'http://localhost:5001';
const BOOK_SERVICE_URL = 'http://localhost:5002';
const LOAN_SERVICE_URL = 'http://localhost:5003';

// DOM Elementleri
const messagesDiv = document.getElementById('messages');
const loginStatusSpan = document.getElementById('login-status');
const bookListDiv = document.getElementById('book-list');
const userLoanListDiv = document.getElementById('user-loan-list');
const userListDiv = document.getElementById('user-list'); // <-- Yeni Kullanıcı Listesi Div'i

// --- Yardımcı Fonksiyonlar --- (showMessage ve apiRequest aynı kalır)
function showMessage(message, type = 'info', duration = 5000) {
    const p = document.createElement('p');
    p.textContent = message;
    p.className = type; // 'success' veya 'error' veya 'info'
    messagesDiv.innerHTML = ''; // Önceki mesajları temizle
    messagesDiv.appendChild(p);
    if (duration > 0) { setTimeout(() => { if (p.parentNode === messagesDiv) { messagesDiv.removeChild(p); } }, duration); }
}

async function apiRequest(url, method = 'GET', body = null) {
    const options = { method: method, headers: {} };
    if (body) { options.headers['Content-Type'] = 'application/json'; options.body = JSON.stringify(body); }
    try {
        const response = await fetch(url, options);
        const responseText = await response.text();
        let data;
        try { data = JSON.parse(responseText); }
        catch(e) {
             if (!response.ok) { throw new Error(`HTTP ${response.status}: ${response.statusText || responseText}`); }
             console.warn("API'den JSON olmayan başarılı yanıt alındı:", responseText);
             data = { message: responseText || "İşlem başarılı (içerik yok)." };
        }
        if (!response.ok) { const errorMessage = data?.error || `HTTP ${response.status}: ${response.statusText}`; throw new Error(errorMessage); }
        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        if (error.message.includes('Failed to fetch')) { throw new Error('API\'ye ulaşılamadı. Servislerin çalıştığından ve CORS ayarlarının doğru olduğundan emin olun.'); }
        throw new Error(error.message || 'Bilinmeyen bir API hatası oluştu.');
    }
}


// --- Event Listeners ---

// Kullanıcı Kayıt (Aynı kalır)
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault(); const button = e.target.querySelector('button'); button.disabled = true;
    const username = document.getElementById('reg-username').value; const email = document.getElementById('reg-email').value; const password = document.getElementById('reg-password').value;
    try { const result = await apiRequest(`${USER_SERVICE_URL}/users/register`, 'POST', { username, email, password }); showMessage(`Kullanıcı '${result.username}' (ID: ${result.user_id}) başarıyla kaydedildi!`, 'success'); e.target.reset(); document.getElementById('list-users-btn').click(); /* Listeyi yenile */ } catch (error) { showMessage(`Kayıt Hatası: ${error.message}`, 'error'); } finally { button.disabled = false; }
});

// Kullanıcı Giriş (Aynı kalır)
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault(); const button = e.target.querySelector('button'); button.disabled = true;
    const username = document.getElementById('login-username').value; const password = document.getElementById('login-password').value; loginStatusSpan.textContent = '';
    try { const result = await apiRequest(`${USER_SERVICE_URL}/users/login`, 'POST', { username, password }); showMessage(`Hoşgeldin, ${result.user.username}! Giriş başarılı.`, 'success'); loginStatusSpan.textContent = `(Giriş Yapıldı - ID: ${result.user.user_id})`; e.target.reset(); } catch (error) { showMessage(`Giriş Hatası: ${error.message}`, 'error'); } finally { button.disabled = false; }
});

// Kullanıcıları Listele (YENİ)
document.getElementById('list-users-btn').addEventListener('click', async () => {
    const button = document.getElementById('list-users-btn');
    button.disabled = true;
    userListDiv.innerHTML = '<p class="list-placeholder">Kullanıcılar yükleniyor...</p>';
    try {
        const users = await apiRequest(`${USER_SERVICE_URL}/users`, 'GET');
        if (!Array.isArray(users)) { throw new Error("API'den geçerli kullanıcı listesi alınamadı."); }
        if (users.length === 0) { userListDiv.innerHTML = '<p class="list-placeholder">Sistemde kayıtlı kullanıcı bulunamadı.</p>'; return; }
        let html = '<ul>';
        users.forEach(user => {
            html += `<li>
                        <div class="item-info"><strong>${user.username}</strong></div>
                        <div class="item-details">ID: ${user.user_id} | E-posta: ${user.email}</div>
                     </li>`;
        });
        html += '</ul>';
        userListDiv.innerHTML = html;
    } catch (error) {
        showMessage(`Kullanıcı Listeleme Hatası: ${error.message}`, 'error');
        userListDiv.innerHTML = `<p class="error list-placeholder">Kullanıcılar yüklenemedi.</p>`;
    } finally {
        button.disabled = false;
    }
});


// Yeni Kitap Ekle (ISBN kaldırıldı)
document.getElementById('add-book-form').addEventListener('submit', async (e) => {
    e.preventDefault(); const button = e.target.querySelector('button'); button.disabled = true;
    const title = document.getElementById('book-title').value;
    const author = document.getElementById('book-author').value;
    // const isbn = document.getElementById('book-isbn').value; // KALDIRILDI
    const quantity = parseInt(document.getElementById('book-quantity').value, 10) || 1;

    // ISBN backend'de zorunlu olduğu için rastgele bir tane üretebiliriz (test için)
    // Veya kullanıcıdan alıp backend'e göndermeye devam edip sadece arayüzde göstermeyebiliriz.
    // Şimdilik backend'in hala ISBN beklediğini varsayalım ve rastgele gönderelim:
    const randomIsbn = `TEST-${Math.random().toString(36).substring(2, 15)}`; // Test amaçlı
    if (!title || !author) { // ISBN kontrolü kalktı
         showMessage('Başlık ve Yazar alanları zorunludur.', 'error');
         button.disabled = false; return;
    }

    try {
        // Backend hala ISBN bekliyor, o yüzden gönderiyoruz ama arayüzde sormadık.
        const result = await apiRequest(`${BOOK_SERVICE_URL}/books`, 'POST', { title, author, isbn: randomIsbn, quantity });
        showMessage(`Kitap '${result.title}' (ID: ${result.book_id}) başarıyla eklendi!`, 'success');
        e.target.reset(); document.getElementById('list-books-btn').click();
    } catch (error) {
        showMessage(`Kitap Ekleme Hatası: ${error.message}`, 'error');
    } finally {
        button.disabled = false;
    }
});

// Kitapları Listele (ISBN gösterimi kaldırıldı)
document.getElementById('list-books-btn').addEventListener('click', async () => {
    const button = document.getElementById('list-books-btn');
    button.disabled = true;
    bookListDiv.innerHTML = '<p class="list-placeholder">Kitaplar yükleniyor...</p>';
    try {
        const books = await apiRequest(`${BOOK_SERVICE_URL}/books`, 'GET');
        if (!Array.isArray(books)) { throw new Error("API'den geçerli kitap listesi alınamadı."); }
        if (books.length === 0) { bookListDiv.innerHTML = '<p class="list-placeholder">Katalogda hiç kitap bulunamadı.</p>'; return; }
        let html = '<ul>';
        books.forEach(book => {
            html += `<li>
                        <div class="item-info"><strong>${book.title}</strong> / ${book.author}</div>
                        <div class="item-details">ID: ${book.book_id} | Stok: ${book.quantity} | Mevcut: ${book.available_quantity}</div>
                     </li>`; // ISBN gösterimi kaldırıldı
        });
        html += '</ul>';
        bookListDiv.innerHTML = html;
    } catch (error) {
        showMessage(`Kitap Listeleme Hatası: ${error.message}`, 'error');
        bookListDiv.innerHTML = `<p class="error list-placeholder">Kitaplar yüklenemedi.</p>`;
    } finally {
        button.disabled = false;
    }
});

// Ödünç Alma/İade ve Kullanıcı Ödünçleri Listeleme (Aynı kalır)
// Kitap Ödünç Al
document.getElementById('borrow-form').addEventListener('submit', async (e) => {
    e.preventDefault(); const button = e.target.querySelector('button'); button.disabled = true;
    const userId = parseInt(document.getElementById('borrow-user-id').value, 10); const bookId = parseInt(document.getElementById('borrow-book-id').value, 10);
    if (isNaN(userId) || isNaN(bookId)) { showMessage('Lütfen geçerli Kullanıcı ID ve Kitap ID girin.', 'error'); button.disabled = false; return; }
    try { const result = await apiRequest(`${LOAN_SERVICE_URL}/loans`, 'POST', { user_id: userId, book_id: bookId }); showMessage(`Kitap (ID: ${bookId}), Kullanıcı (ID: ${userId}) tarafından başarıyla ödünç alındı. Loan ID: ${result.loan_id}`, 'success'); e.target.reset(); document.getElementById('list-books-btn').click(); const userLoansInput = document.getElementById('user-loans-id'); if(userLoansInput.value && parseInt(userLoansInput.value, 10) === userId) { document.getElementById('list-user-loans-btn').click(); } } catch (error) { showMessage(`Ödünç Alma Hatası: ${error.message}`, 'error'); } finally { button.disabled = false; }
});
// Kitap İade Et
document.getElementById('return-form').addEventListener('submit', async (e) => {
    e.preventDefault(); const button = e.target.querySelector('button'); button.disabled = true;
    const loanId = parseInt(document.getElementById('return-loan-id').value, 10);
    if (isNaN(loanId)) { showMessage('Lütfen geçerli bir Ödünç ID (Loan ID) girin.', 'error'); button.disabled = false; return; }
    try { const result = await apiRequest(`${LOAN_SERVICE_URL}/loans/${loanId}/return`, 'PUT'); showMessage(`Ödünç (ID: ${loanId}) başarıyla iade edildi. Durum: ${result.status}`, 'success'); e.target.reset(); document.getElementById('list-books-btn').click(); const userLoansInput = document.getElementById('user-loans-id'); if(userLoansInput.value && parseInt(userLoansInput.value, 10) === result.user_id) { document.getElementById('list-user-loans-btn').click(); } else { userLoanListDiv.innerHTML = '<p class="list-placeholder">Kullanıcının ödünç listesini görmek için ID girip butona tıklayın.</p>'; } } catch (error) { showMessage(`İade Hatası: ${error.message}`, 'error'); } finally { button.disabled = false; }
});
// Kullanıcının Ödünçlerini Listele
document.getElementById('list-user-loans-btn').addEventListener('click', async () => {
    const button = document.getElementById('list-user-loans-btn'); button.disabled = true; const userId = parseInt(document.getElementById('user-loans-id').value, 10); userLoanListDiv.innerHTML = '<p class="list-placeholder">Yükleniyor...</p>';
    if (isNaN(userId)) { showMessage('Lütfen geçerli bir Kullanıcı ID girin.', 'error'); userLoanListDiv.innerHTML = '<p class="list-placeholder">Kullanıcının ödünç listesini görmek için ID girip butona tıklayın.</p>'; button.disabled = false; return; }
    try { const loans = await apiRequest(`${LOAN_SERVICE_URL}/loans/user/${userId}`, 'GET'); if (!Array.isArray(loans)) { throw new Error("API'den geçerli ödünç listesi alınamadı."); } if (loans.length === 0) { userLoanListDiv.innerHTML = `<p class="list-placeholder">Kullanıcı (ID: ${userId}) hiç kitap ödünç almamış veya hepsi iade edilmiş.</p>`; return; } let html = '<ul>'; loans.forEach(loan => { const loanDate = loan.loan_date ? new Date(loan.loan_date).toLocaleDateString() : 'N/A'; const dueDate = loan.due_date ? new Date(loan.due_date).toLocaleDateString() : 'N/A'; const returnDate = loan.return_date ? `(İade: ${new Date(loan.return_date).toLocaleDateString()})` : ''; html += `<li><div class="item-info"><strong>Loan ID: ${loan.loan_id}</strong> | Kitap ID: ${loan.book_id}</div><div class="item-details">Alınma: ${loanDate} | Son İade: ${dueDate} | Durum: ${loan.status} ${returnDate}</div></li>`; }); html += '</ul>'; userLoanListDiv.innerHTML = html; } catch (error) { showMessage(`Kullanıcı Ödünçleri Listeleme Hatası: ${error.message}`, 'error'); userLoanListDiv.innerHTML = `<p class="error list-placeholder">Ödünçler yüklenemedi.</p>`; } finally { button.disabled = false; }
});

// Sayfa ilk yüklendiğinde kullanıcı ve kitap listelerini otomatik çekebiliriz
document.addEventListener('DOMContentLoaded', () => {
     document.getElementById('list-users-btn').click();
     document.getElementById('list-books-btn').click();
     showMessage('Arayüze hoş geldiniz!', 'info', 3000);
});