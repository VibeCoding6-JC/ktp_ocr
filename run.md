# 🚀 Panduan Menjalankan OCR KTP (Untuk Pemula)

Dokumen ini berisi langkah-langkah lengkap untuk menjalankan aplikasi OCR KTP dari awal.

---

## 📋 Prasyarat

Sebelum memulai, pastikan Anda sudah menginstall:

### 1. Python 3.10 atau lebih baru

**Cara cek apakah Python sudah terinstall:**
```powershell
python --version
```

Jika belum terinstall, download di: https://www.python.org/downloads/

> ⚠️ **PENTING:** Saat install Python, centang opsi **"Add Python to PATH"**

### 2. Dapatkan API Key Gemini (GRATIS)

1. Buka https://aistudio.google.com/app/apikey
2. Login dengan akun Google
3. Klik **"Create API Key"**
4. Copy API key yang muncul (simpan di tempat aman)

---

## 🔧 Langkah-Langkah Instalasi

### Langkah 1: Buka Terminal/PowerShell

1. Buka **File Explorer**
2. Navigasi ke folder `D:\VibeCode Day1\ocr-ktp`
3. Klik kanan di area kosong
4. Pilih **"Open in Terminal"** atau **"Open PowerShell window here"**

Atau buka PowerShell dan ketik:
```powershell
cd "D:\VibeCode Day1\ocr-ktp"
```

---

### Langkah 2: Buat Virtual Environment

Virtual environment adalah "ruang terisolasi" untuk install library Python tanpa mengganggu sistem.

```powershell
python -m venv venv
```

Tunggu beberapa detik sampai selesai.

---

### Langkah 3: Aktifkan Virtual Environment

```powershell
.\venv\Scripts\activate
```

✅ **Tanda berhasil:** Akan muncul `(venv)` di awal baris terminal seperti ini:
```
(venv) PS D:\VibeCode Day1\ocr-ktp>
```

> ⚠️ **Jika ada error "execution policy"**, jalankan perintah ini dulu:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Kemudian ulangi langkah 3.

---

### Langkah 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

Tunggu sampai semua library terinstall (mungkin butuh 1-2 menit).

✅ **Tanda berhasil:** Tidak ada pesan error merah.

---

### Langkah 5: Buat File Konfigurasi (.env)

**Cara 1 - Menggunakan PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Cara 2 - Manual:**
1. Buka File Explorer
2. Copy file `.env.example`
3. Paste dan rename menjadi `.env`

---

### Langkah 6: Masukkan API Key Gemini

1. Buka file `.env` dengan Notepad atau VS Code
2. Ganti `your_gemini_api_key_here` dengan API key Anda

**Sebelum:**
```
GEMINI_API_KEY=your_gemini_api_key_here
```

**Sesudah:**
```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

3. **Simpan file** (Ctrl+S)

---

### Langkah 7: Jalankan Aplikasi

```powershell
uvicorn app.main:app --reload
```

✅ **Tanda berhasil:** Akan muncul pesan seperti ini:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

---

## 🌐 Mengakses Aplikasi

Setelah aplikasi berjalan, buka browser dan akses:

| URL | Keterangan |
|-----|------------|
| http://localhost:8000 | Halaman utama API |
| http://localhost:8000/docs | **Swagger UI** - untuk testing API |
| http://localhost:8000/redoc | Dokumentasi API alternatif |

---

## 🧪 Cara Testing OCR KTP

### Menggunakan Swagger UI (Recommended untuk pemula)

1. Buka http://localhost:8000/docs
2. Klik pada endpoint **POST /api/v1/ocr/ktp**
3. Klik tombol **"Try it out"**
4. Klik **"Choose File"** dan pilih foto KTP
5. Klik **"Execute"**
6. Lihat hasil di bagian **"Response body"**

### Menggunakan cURL (Terminal)

```powershell
curl -X POST "http://localhost:8000/api/v1/ocr/ktp" -H "Content-Type: multipart/form-data" -F "file=@C:\path\to\ktp.jpg"
```

Ganti `C:\path\to\ktp.jpg` dengan path file KTP Anda.

---

## 🛑 Cara Menghentikan Aplikasi

Tekan **Ctrl + C** di terminal untuk menghentikan server.

---

## 🔄 Menjalankan Ulang (Setelah Restart Komputer)

Setiap kali ingin menjalankan ulang aplikasi:

```powershell
# 1. Buka terminal dan masuk ke folder proyek
cd "D:\VibeCode Day1\ocr-ktp"

# 2. Aktifkan virtual environment
.\venv\Scripts\activate

# 3. Jalankan aplikasi
uvicorn app.main:app --reload
```

---

## ❓ Troubleshooting (Masalah Umum)

### 1. Error: "python is not recognized"
**Solusi:** Python belum terinstall atau belum ditambahkan ke PATH. Install ulang Python dan centang "Add Python to PATH".

### 2. Error: "execution policy"
**Solusi:** Jalankan perintah ini:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Error: "GEMINI_API_KEY tidak ditemukan"
**Solusi:** Pastikan file `.env` sudah dibuat dan API key sudah diisi dengan benar.

### 4. Error: "Address already in use"
**Solusi:** Port 8000 sudah digunakan. Gunakan port lain:
```powershell
uvicorn app.main:app --reload --port 8001
```
Kemudian akses di http://localhost:8001

### 5. Error saat install requirements
**Solusi:** Coba upgrade pip dulu:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📞 Butuh Bantuan?

Jika masih mengalami kendala, pastikan:
1. Python versi 3.10+ sudah terinstall
2. Virtual environment sudah aktif (ada `(venv)` di terminal)
3. File `.env` sudah dibuat dan berisi API key yang valid
4. Semua dependencies sudah terinstall tanpa error

---

## 📝 Ringkasan Perintah

```powershell
# Sekali saja (instalasi awal)
cd "D:\VibeCode Day1\ocr-ktp"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit file .env dan masukkan API key

# Setiap kali menjalankan
cd "D:\VibeCode Day1\ocr-ktp"
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

Selamat mencoba! 🎉
