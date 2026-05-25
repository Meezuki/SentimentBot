import discord
import os
import torch
import re
import torch.nn.functional as F
import datetime
from transformers import BertTokenizer, BertForSequenceClassification
from dotenv import load_dotenv

# 1. Load Token secara Aman
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ Error: Token Discord tidak ditemukan di file .env!")
    exit()

# 2. Inisialisasi Model IDTM
MODEL_PATH = "./idtm-indobert-model"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"Memuat otak IDTM ke memori ({device})...")
try:
    tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
    model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
    model.to(device)
    model.eval()
except Exception as e:
    print(f"❌ Gagal memuat model: {e}")
    exit()

id2label = {0: "Neutral", 1: "Violence", 2: "Racist", 3: "Harassment"}

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'@[^\s]+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def predict_toxicity(text):
    cleaned = clean_text(text)
    if not cleaned:
        return "Neutral", 100.0
        
    inputs = tokenizer(cleaned, return_tensors="pt", truncation=True, max_length=128, padding=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1).squeeze()
        
        predicted_class_id = torch.argmax(probs).item()
        confidence = probs[predicted_class_id].item() * 100
        
    return id2label[predicted_class_id], confidence

# 3. Konfigurasi Klien Discord
intents = discord.Intents.default()
intents.message_content = True  # Wajib diaktifkan di Discord Developer Portal
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("="*50)
    print(f"✅ Login berhasil sebagai: {client.user}")
    print("Sistem IDTM siap dideploy dan memantau server Advisory D7041 Faisal.")
    print("="*50)

@client.event
async def on_message(message):
    # Bot tidak boleh merespons pesannya sendiri
    if message.author == client.user:
        return

    # ==========================================
    # FITUR COMMAND: !logs
    # ==========================================
    if message.content.startswith("!logs"):
        # Opsional: Batasi hanya Admin atau pengguna dengan izin "Manage Messages" yang bisa melihat log
        if not message.author.guild_permissions.manage_messages:
            await message.channel.send("❌ **Akses Ditolak!** Hanya tim moderator yang dapat mengakses log ini.")
            return
            
        # Cek apakah file log sudah ada
        if not os.path.exists("toxicity_logs.txt"):
            await message.channel.send("📭 Belum ada riwayat chat toksik yang tercatat.")
            return
            
        # Baca isi file log
        with open("toxicity_logs.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not lines:
            await message.channel.send("📭 Log saat ini masih kosong.")
            return
            
        # Ambil 10 log terakhir agar tidak melebihi batas 2000 karakter Discord
        recent_logs = "".join(lines[-10:])
        
        # Kirim log ke channel
        await message.channel.send(f"**📜 10 Log Toksisitas Terakhir:**\n```text\n{recent_logs}\n```")
        return

    # ==========================================
    # FITUR UTAMA: DETEKSI TOKSISITAS
    # ==========================================
    # Lakukan prediksi pada teks yang masuk
    label, confidence = predict_toxicity(message.content)

    # Bot hanya bereaksi jika pesan terdeteksi toksik DAN keyakinan model > 75%
    if label != "Neutral" and confidence > 75.0:
        
        # 1. Simpan data ke dalam file teks (sebagai database lokal sederhana)
        waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # log_entry = f"[{waktu_sekarang}] {message.author.name} | Label: {label} ({confidence:.2f}%)\n"

        pesan_asli = message.content.replace('\n', ' ')
        log_entry = f"[{waktu_sekarang}] {message.author.name} | Pesan: \"{pesan_asli}\" | Label: {label} ({confidence:.2f}%)\n"

        
        with open("toxicity_logs.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)

        # 2. Kirim peringatan publik ke channel
        log_reply = (
            f"⚠️ **Peringatan Moderasi Otomatis!** ⚠️\n"
            f"> **Username:** `{message.author.name}`\n"
            f"> **Sentiment:** `{label}`\n"
            f"> **Keyakinan:** `{confidence:.2f}%`\n"
            f"Pesan Anda telah dicatat oleh sistem."
        )
        
        await message.channel.send(log_reply)

# Menjalankan bot
client.run(TOKEN)