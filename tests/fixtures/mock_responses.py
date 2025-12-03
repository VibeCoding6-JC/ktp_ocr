"""
Mock responses for testing.

Contains sample Gemini API responses and KTP data.
"""

# Sample valid KTP data
VALID_KTP_RESPONSE = {
    "nik": "3201234567890001",
    "nama": "JOHN DOE",
    "tempat_lahir": "JAKARTA",
    "tanggal_lahir": "01-01-1990",
    "jenis_kelamin": "LAKI-LAKI",
    "alamat": "JL. CONTOH NO. 123",
    "rt_rw": "001/002",
    "kelurahan_desa": "CONTOH",
    "kecamatan": "KECAMATAN CONTOH",
    "agama": "ISLAM",
    "status_perkawinan": "BELUM KAWIN",
    "pekerjaan": "KARYAWAN SWASTA",
    "kewarganegaraan": "WNI",
    "berlaku_hingga": "SEUMUR HIDUP"
}

# Sample partial KTP data (low quality image)
PARTIAL_KTP_RESPONSE = {
    "nik": "3201234567890001",
    "nama": "JANE DOE",
    "tempat_lahir": "BANDUNG",
    "tanggal_lahir": None,
    "jenis_kelamin": "PEREMPUAN",
    "alamat": None,
    "rt_rw": None,
    "kelurahan_desa": None,
    "kecamatan": None,
    "agama": "KRISTEN",
    "status_perkawinan": None,
    "pekerjaan": None,
    "kewarganegaraan": "WNI",
    "berlaku_hingga": None
}

# Sample KTP with invalid NIK
INVALID_NIK_RESPONSE = {
    "nik": "123",
    "nama": "INVALID PERSON",
    "tempat_lahir": "SURABAYA",
    "tanggal_lahir": "15-06-1985",
    "jenis_kelamin": "LAKI-LAKI",
    "alamat": "JL. TEST",
    "rt_rw": "001/001",
    "kelurahan_desa": "TEST",
    "kecamatan": "TEST",
    "agama": "ISLAM",
    "status_perkawinan": "KAWIN",
    "pekerjaan": "PNS",
    "kewarganegaraan": "WNI",
    "berlaku_hingga": "SEUMUR HIDUP"
}

# Sample female KTP
FEMALE_KTP_RESPONSE = {
    "nik": "3201234567890002",
    "nama": "SITI AMINAH",
    "tempat_lahir": "SURABAYA",
    "tanggal_lahir": "15-03-1995",
    "jenis_kelamin": "PEREMPUAN",
    "alamat": "JL. MAWAR NO. 45",
    "rt_rw": "003/005",
    "kelurahan_desa": "SUKAMAJU",
    "kecamatan": "KEBAYORAN",
    "agama": "ISLAM",
    "status_perkawinan": "KAWIN",
    "pekerjaan": "IBU RUMAH TANGGA",
    "kewarganegaraan": "WNI",
    "berlaku_hingga": "SEUMUR HIDUP"
}

# Gemini response with markdown wrapper
def get_gemini_markdown_response(data: dict) -> str:
    """Generate Gemini response with markdown code block."""
    import json
    return f"```json\n{json.dumps(data, indent=2)}\n```"

# Gemini response as plain JSON
def get_gemini_json_response(data: dict) -> str:
    """Generate Gemini response as plain JSON."""
    import json
    return json.dumps(data)

# Error responses
GEMINI_ERROR_RESPONSES = {
    "rate_limit": "API rate limit exceeded. Please try again later.",
    "invalid_image": "Unable to process the image. The image may be corrupted.",
    "no_ktp_detected": "No KTP detected in the image.",
    "low_quality": "Image quality too low to extract data accurately.",
}
