1. Deskripsi Singkat
Y adalah aplikasi sosial media berbasis web yang dirancang menyerupai beberapa fungsionalitas dari media sosial Twitter/X.

2. Tujuan Aplikasi
Tujuan utama aplikasi ini adalah menyediakan platform bagi pengguna untuk:
  a. Berbagi pemikiran atau status (Tweet) secara real-time.
  b. Berinteraksi dengan konten pengguna lain melalui fitur "Like".
  c. Menikmati pengalaman pengguna yang nyaman dengan dukungan tema gelap dan terang.

3. Fitur Utama
  a. Membuat akun dan login app sesuai credential
  b. Posting, Edit, Hapus Tweet
  c. Like Tweet
  d. Melihat profil, bio, status, statistik follower-following
  e. Follow mechanism
  f. Memperlihatkan timeline
  g. Fitur tema (Dark/Light Mode)

4. Struktur Direktori
Final-Project/
├── kusutkusut-backend/ # Backend
│   ├── kusutkusut/           
│   ├── main/                 
│   ├── db.sqlite3            
│   └── manage.py             
│
├── home.html # Home page
├── login.html # Login page
├── sign_in.html # Registration page
├── profile.html # Profile page
├── compose.html # Create tweet page
└── style.css # Styling (CSS)

5. Cara Menjalankan Aplikasi

BACKEND
  1. Buka terminal/command prompt.
  2. Masuk ke direktori backend: cd kusutkusut-backend
  3. Jalankan server: python manage.py runserver
  4. Server akan berjalan di http://127.0.0.1:8000/

FRONTEND
  1. Buka login.html
