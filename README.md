# OCR KTP dengan Gemini Flash

API untuk mengekstrak data dari foto KTP (Kartu Tanda Penduduk) Indonesia menggunakan Google Gemini Flash.

## 🚀 Fitur

- ✅ Ekstraksi data KTP otomatis (NIK, Nama, Alamat, dll.)
- ✅ Validasi format gambar (JPG, PNG, WEBP)
- ✅ Validasi ukuran file
- ✅ Response terstruktur dalam format JSON
- ✅ Dokumentasi API interaktif (Swagger UI)

## 📋 Data yang Diekstrak

| Field | Keterangan |
|-------|------------|
| NIK | Nomor Induk Kependudukan (16 digit) |
| Nama | Nama lengkap |
| Tempat/Tanggal Lahir | Tempat dan tanggal lahir |
| Jenis Kelamin | Laki-laki / Perempuan |
| Alamat | Alamat lengkap |
| RT/RW | Nomor RT dan RW |
| Kelurahan/Desa | Nama kelurahan atau desa |
| Kecamatan | Nama kecamatan |
| Agama | Agama |
| Status Perkawinan | Status perkawinan |
| Pekerjaan | Jenis pekerjaan |
| Kewarganegaraan | WNI / WNA |
| Berlaku Hingga | Masa berlaku KTP |

## 🛠️ Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd ocr-ktp
```

### 2. Buat Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment

```bash
# Copy file contoh
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit file .env dan masukkan API key Gemini Anda
```

Dapatkan API key Gemini di: https://aistudio.google.com/app/apikey

### 5. Jalankan Aplikasi

```bash
# Development mode
uvicorn app.main:app --reload

# Atau
python -m app.main
```

Aplikasi akan berjalan di: http://localhost:8000

## 📖 Dokumentasi API

Setelah aplikasi berjalan, akses dokumentasi di:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Penggunaan API

### Endpoint: POST `/api/v1/ocr/ktp`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/ktp" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/ktp.jpg"
```

**Response Success:**
```json
{
  "success": true,
  "data": {
    "nik": "3201234567890001",
    "nama": "JOHN DOE",
    "tempat_lahir": "JAKARTA",
    "tanggal_lahir": "01-01-1990",
    "jenis_kelamin": "LAKI-LAKI",
    "alamat": "JL. CONTOH NO. 123",
    "rt_rw": "001/002",
    "kelurahan_desa": "CONTOH",
    "kecamatan": "CONTOH",
    "agama": "ISLAM",
    "status_perkawinan": "BELUM KAWIN",
    "pekerjaan": "KARYAWAN SWASTA",
    "kewarganegaraan": "WNI",
    "berlaku_hingga": "SEUMUR HIDUP"
  },
  "confidence": 0.95,
  "message": "Data berhasil diekstrak"
}
```

## 📁 Struktur Proyek

```
ocr-ktp/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Konfigurasi
│   ├── routers/
│   │   └── ocr.py           # Router OCR endpoint
│   ├── services/
│   │   └── gemini_service.py # Service Gemini API
│   ├── models/
│   │   └── ktp.py           # Pydantic models
│   └── utils/
│       └── image_utils.py   # Utility gambar
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚠️ Catatan Penting

1. **Privasi Data**: Data KTP adalah data sensitif. Aplikasi ini tidak menyimpan gambar atau data setelah diproses.
2. **Kualitas Gambar**: Hasil OCR bergantung pada kualitas gambar. Pastikan gambar jelas dan tidak buram.
3. **API Key**: Jangan commit file `.env` yang berisi API key ke repository.

## 📄 Lisensi

MIT License
