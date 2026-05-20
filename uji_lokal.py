import torch
import re
import torch.nn.functional as F
from transformers import BertTokenizer, BertForSequenceClassification

# 1. Path ke folder model lokal hasil ekstrak
MODEL_PATH = "./idtm-indobert-model"

print("Sedang memuat model IndoBERT dari folder lokal...")

try:
    # Memuat tokenizer dan arsitektur model dari folder lokal
    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
    model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
except Exception as e:
    print(f"Gagal memuat model. Pastikan folder '{MODEL_PATH}' berada di direktori yang benar.")
    print(f"Detail Error: {e}")
    exit()

# Setup hardware (Otomatis menggunakan GPU jika setup CUDA sudah aktif, jika tidak kembali ke CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Mapping ID label ke nama kategori asli proyek IDTM
id2label = {0: "Neutral", 1: "Violence", 2: "Racist", 3: "Harassment"}

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'@[^\s]+', '', text) # Hapus @mention
    text = re.sub(r'[^\w\s]', '', text) # Hapus tanda baca
    return text.strip()

def prediksi_chat(text):
    cleaned = clean_text(text)
    if not cleaned:
        return "Neutral", 100.0, ""
        
    # Proses tokenisasi kalimat input
    inputs = tokenizer(cleaned, return_tensors="pt", truncation=True, max_length=128, padding=True)
    
    # Proteksi device: Mengirim input tepat ke lokasi model berada (CPU/GPU)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=1).squeeze()
        
        # Mengambil ID kelas dengan probabilitas keyakinan tertinggi
        predicted_class_id = torch.argmax(probs).item()
        confidence_score = probs[predicted_class_id].item() * 100
        
        label_text = id2label[predicted_class_id]
        
    return label_text, confidence_score, cleaned

print(f"\nSistem monitor aktif menggunakan: {device}")
print("="*60)
print("Model IDTM Berhasil Dimuat di Komputer Lokal")
print("Ketik 'keluar' untuk menghentikan program.")
print("="*60)

while True:
    pesan = input("\nMasukkan pesan teks: ")
    
    if pesan.lower() == 'keluar':
        print("Sistem dinonaktifkan. Sampai jumpa!")
        break
        
    label, confidence, teks_bersih = prediksi_chat(pesan)
    
    print(f"[Teks Bersih] : {teks_bersih}")
    print(f"[Prediksi]    : {label}")
    print(f"[Keyakinan]   : {confidence:.2f}%")