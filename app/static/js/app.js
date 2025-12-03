/**
 * OCR KTP Application - Main JavaScript
 * 
 * Handles:
 * - Drag & drop file upload
 * - Image preview
 * - API communication
 * - Result display
 * - Copy & Download functionality
 */

// =============================================================================
// CONSTANTS
// =============================================================================

const API_ENDPOINT = '/api/v1/ocr/ktp';
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

const FIELD_LABELS = {
    nik: 'NIK',
    nama: 'Nama',
    tempat_lahir: 'Tempat Lahir',
    tanggal_lahir: 'Tanggal Lahir',
    jenis_kelamin: 'Jenis Kelamin',
    alamat: 'Alamat',
    rt_rw: 'RT/RW',
    kelurahan_desa: 'Kelurahan/Desa',
    kecamatan: 'Kecamatan',
    agama: 'Agama',
    status_perkawinan: 'Status Perkawinan',
    pekerjaan: 'Pekerjaan',
    kewarganegaraan: 'Kewarganegaraan',
    berlaku_hingga: 'Berlaku Hingga'
};


// =============================================================================
// STATE
// =============================================================================

let selectedFile = null;
let extractedData = null;


// =============================================================================
// DOM ELEMENTS
// =============================================================================

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadPrompt = document.getElementById('uploadPrompt');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const processBtn = document.getElementById('processBtn');
const processBtnText = document.getElementById('processBtnText');
const processBtnSpinner = document.getElementById('processBtnSpinner');
const clearBtn = document.getElementById('clearBtn');
const resultCard = document.getElementById('resultCard');
const resultTable = document.getElementById('resultTable');
const confidenceValue = document.getElementById('confidenceValue');
const resultMessage = document.getElementById('resultMessage');
const errorCard = document.getElementById('errorCard');
const errorMessage = document.getElementById('errorMessage');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');
const helpBtn = document.getElementById('helpBtn');
const helpModal = document.getElementById('helpModal');
const closeHelpBtn = document.getElementById('closeHelpBtn');
const toastContainer = document.getElementById('toastContainer');


// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Format file size to human readable string
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
    
    toast.className = `toast ${bgColor} text-white px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2`;
    toast.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            ${type === 'success' 
                ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />'
                : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />'
            }
        </svg>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * Validate file
 */
function validateFile(file) {
    if (!file) {
        return { valid: false, error: 'Tidak ada file yang dipilih' };
    }
    
    if (!ALLOWED_TYPES.includes(file.type)) {
        return { valid: false, error: 'Format file tidak didukung. Gunakan JPG, PNG, atau WEBP.' };
    }
    
    if (file.size > MAX_FILE_SIZE) {
        return { valid: false, error: 'Ukuran file melebihi 5MB.' };
    }
    
    return { valid: true };
}


// =============================================================================
// FILE HANDLING
// =============================================================================

/**
 * Handle file selection
 */
function handleFile(file) {
    const validation = validateFile(file);
    
    if (!validation.valid) {
        showToast(validation.error, 'error');
        return;
    }
    
    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        uploadPrompt.classList.add('hidden');
        imagePreview.classList.remove('hidden');
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        dropZone.classList.add('has-file');
    };
    reader.readAsDataURL(file);
    
    // Enable process button
    processBtn.disabled = false;
    clearBtn.classList.remove('hidden');
    
    // Hide previous results
    hideResults();
}

/**
 * Clear selected file
 */
function clearFile() {
    selectedFile = null;
    extractedData = null;
    fileInput.value = '';
    
    previewImg.src = '';
    uploadPrompt.classList.remove('hidden');
    imagePreview.classList.add('hidden');
    dropZone.classList.remove('has-file');
    
    processBtn.disabled = true;
    clearBtn.classList.add('hidden');
    
    hideResults();
}

/**
 * Hide result cards
 */
function hideResults() {
    resultCard.classList.add('hidden');
    errorCard.classList.add('hidden');
}


// =============================================================================
// API COMMUNICATION
// =============================================================================

/**
 * Process OCR
 */
async function processOCR() {
    if (!selectedFile) {
        showToast('Pilih file terlebih dahulu', 'error');
        return;
    }
    
    // Set loading state
    setLoading(true);
    hideResults();
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showResult(result);
        } else {
            showError(result.message || result.error || 'Terjadi kesalahan saat memproses gambar');
        }
    } catch (error) {
        console.error('OCR Error:', error);
        showError('Gagal menghubungi server. Pastikan koneksi internet Anda stabil.');
    } finally {
        setLoading(false);
    }
}

/**
 * Set loading state
 */
function setLoading(loading) {
    processBtn.disabled = loading;
    
    if (loading) {
        processBtnText.textContent = 'Memproses...';
        processBtnSpinner.classList.remove('hidden');
    } else {
        processBtnText.textContent = 'Proses OCR';
        processBtnSpinner.classList.add('hidden');
    }
}


// =============================================================================
// RESULT DISPLAY
// =============================================================================

/**
 * Show OCR result
 */
function showResult(result) {
    extractedData = result;
    
    // Update confidence
    const confidence = Math.round((result.confidence || 0) * 100);
    confidenceValue.textContent = confidence + '%';
    
    // Update confidence badge color
    const badge = document.getElementById('confidenceBadge').querySelector('span');
    if (confidence >= 80) {
        badge.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800';
    } else if (confidence >= 50) {
        badge.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800';
    } else {
        badge.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800';
    }
    
    // Build table rows
    let tableHTML = '';
    for (const [key, label] of Object.entries(FIELD_LABELS)) {
        const value = result.data?.[key] || '-';
        tableHTML += `
            <tr class="hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-500 font-medium w-1/3">${label}</td>
                <td class="px-4 py-3 text-gray-800">${value}</td>
            </tr>
        `;
    }
    resultTable.innerHTML = tableHTML;
    
    // Show message if available
    if (result.message) {
        resultMessage.textContent = result.message;
        resultMessage.classList.remove('hidden');
    } else {
        resultMessage.classList.add('hidden');
    }
    
    // Show result card
    resultCard.classList.remove('hidden');
    errorCard.classList.add('hidden');
    
    showToast('Data berhasil diekstrak!', 'success');
}

/**
 * Show error
 */
function showError(message) {
    errorMessage.textContent = message;
    errorCard.classList.remove('hidden');
    resultCard.classList.add('hidden');
    
    showToast('Gagal memproses gambar', 'error');
}


// =============================================================================
// COPY & DOWNLOAD
// =============================================================================

/**
 * Copy result to clipboard
 */
async function copyToClipboard() {
    if (!extractedData?.data) {
        showToast('Tidak ada data untuk disalin', 'error');
        return;
    }
    
    try {
        const jsonString = JSON.stringify(extractedData.data, null, 2);
        await navigator.clipboard.writeText(jsonString);
        showToast('Data berhasil disalin ke clipboard!', 'success');
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = JSON.stringify(extractedData.data, null, 2);
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Data berhasil disalin ke clipboard!', 'success');
    }
}

/**
 * Download result as JSON
 */
function downloadJSON() {
    if (!extractedData?.data) {
        showToast('Tidak ada data untuk diunduh', 'error');
        return;
    }
    
    const jsonString = JSON.stringify(extractedData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `ktp_data_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('File JSON berhasil diunduh!', 'success');
}


// =============================================================================
// MODAL
// =============================================================================

function showHelpModal() {
    helpModal.classList.remove('hidden');
    helpModal.classList.add('flex');
}

function hideHelpModal() {
    helpModal.classList.add('hidden');
    helpModal.classList.remove('flex');
}


// =============================================================================
// EVENT LISTENERS
// =============================================================================

// Drag & Drop
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// File Input
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Buttons
processBtn.addEventListener('click', processOCR);
clearBtn.addEventListener('click', clearFile);
copyBtn.addEventListener('click', copyToClipboard);
downloadBtn.addEventListener('click', downloadJSON);

// Help Modal
helpBtn.addEventListener('click', showHelpModal);
closeHelpBtn.addEventListener('click', hideHelpModal);
helpModal.addEventListener('click', (e) => {
    if (e.target === helpModal) {
        hideHelpModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        hideHelpModal();
    }
});


// =============================================================================
// INITIALIZATION
// =============================================================================

console.log('🪪 OCR KTP Application loaded');
