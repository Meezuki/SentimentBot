# IDTM: Indonesian Discord Toxicity Monitor

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Transformers-Hugging%20Face-yellow)](https://huggingface.co/docs/transformers/index)
[![discord.py](https://img.shields.io/badge/discord.py-v2.0%2B-blueviolet)](https://discordpy.readthedocs.io/en/stable/)

**IDTM (Indonesian Discord Toxicity Monitor)** is a Discord bot powered by a fine-tuned IndoBERT model to monitor Discord channels and automatically flag, alert, and log toxic Indonesian comments. It classifies incoming messages into four distinct categories in real-time, helping moderators maintain a healthy and safe community.

---

## 🚀 Features

- **Real-Time Classification**: Automatically analyzes incoming text using a fine-tuned IndoBERT model.
- **Multi-Class Classification**: Categorizes message sentiments/toxicity levels into:
  - `Neutral`
  - `Violence` (Kekerasan)
  - `Racist` (SARA)
  - `Harassment` (Pelecehan / Perundungan)
- **High-Confidence Warnings**: Automatically logs and triggers warnings in the Discord channel when a toxic classification has a confidence score **exceeding 80%**.
- **Audit Logs**: Records toxic occurrences in a simple local database file (`toxicity_logs.txt`) detailing the timestamp, username, message content, classified label, and confidence score.
- **Mod Command**: Provides a restricted `!logs` command enabling server administrators (with `Manage Messages` permission) to fetch the 10 most recent toxic logs directly in Discord.
- **Offline CLI Playground**: Includes `uji_lokal.py` for testing inputs interactively via command line without spinning up the Discord bot.

---

## 📁 Project Structure

```text
SentimentBot/
├── idtm-indobert-model/     # Local directory containing fine-tuned IndoBERT model files (model.safetensors, config.json, etc.)
├── bot_idtm.py              # Main Discord bot application script
├── uji_lokal.py             # CLI-based testing script for offline analysis
├── requirements.txt         # Project dependencies
├── toxicity_logs.txt        # Local database for logging toxic events (auto-generated)
└── .env                     # Local environment file containing credentials (ignored in Git)
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python**: Version `3.8` or newer is recommended.
- **GPU (Optional)**: CUDA-enabled GPU and compatible PyTorch version for accelerated inference. The bot will automatically fallback to CPU if CUDA is unavailable.

### 2. Clone and Setup Environment
Clone the repository and install the dependencies listed in `requirements.txt`:

```bash
# Clone the repository
git clone https://github.com/your-username/SentimentBot.git
cd SentimentBot

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Setup Discord Token
Create a `.env` file in the root of the project (if not already present) and populate it with your Discord Bot Token:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

> [!NOTE]
> Make sure to enable the **Message Content Intent** in your Discord Developer Portal under the bot settings, otherwise the bot will not be able to read incoming channel messages to classify them.

### 4. Verify IndoBERT Model Files
Ensure that the fine-tuned model files exist in `./idtm-indobert-model/`:
- `model.safetensors`
- `config.json`
- `tokenizer.json`
- `tokenizer_config.json`

---

## 💻 Usage

### Local CLI Testing
Before running the bot, you can test the IndoBERT model performance interactively in your terminal:

```bash
python uji_lokal.py
```

*Example interaction:*
```text
Sedang memuat model IndoBERT dari folder lokal...

Sistem monitor aktif menggunakan: cuda
============================================================
Model IDTM Berhasil Dimuat di Komputer Lokal
Ketik 'keluar' untuk menghentikan program.
============================================================

Masukkan pesan teks: halo apa kabar semua?
[Teks Bersih] : halo apa kabar semua
[Prediksi]    : Neutral
[Keyakinan]   : 99.87%

Masukkan pesan teks: dasar bocah anjing lu
[Teks Bersih] : dasar bocah anjing lu
[Prediksi]    : Violence
[Keyakinan]   : 98.87%
```

### Running the Discord Bot
Run the following command to log in and start the live moderation bot:

```bash
python bot_idtm.py
```

Upon successful startup, the console will print:
```text
==================================================
✅ Login berhasil sebagai: IDTMBot#1234
Sistem IDTM siap dideploy dan memantau server Advisory D7041 Faisal.
==================================================
```

---

## 🛡️ Moderation Workflow

1. **Message Interception**: The bot monitors channel chat events.
2. **Text Cleansing**: Removes user mentions (e.g. `@Username`), converts text to lowercase, and strips punctuation.
3. **Inference**: Predicts toxicity category and confidence.
4. **Trigger Alert**: If class $\neq$ `Neutral` and confidence score $> 80\%$, the bot:
   - Appends a new line entry to [toxicity_logs.txt](file:///d:/SentimentBot/toxicity_logs.txt).
   - Replies to the channel with a warning message pointing out the user, classification label, and confidence score.

### Example Warning Reply
> ⚠️ **Peringatan Moderasi Otomatis!** ⚠️
> > **Username:** `blues25`
> > **Sentiment:** `Harassment`
> > **Keyakinan:** `99.67%`
>
> Pesan Anda telah dicatat oleh sistem.

---

## 👮 Admin & Moderator Commands

### `!logs`
Fetch and print the **last 10 toxicity alerts** logged by the system.
- **Permission required**: Users must have the `Manage Messages` server permission.
- **Output**: Returns formatted text block of entries directly inside the channel.

---

## 📝 Logging Format
All flagged messages are stored in [toxicity_logs.txt](file:///d:/SentimentBot/toxicity_logs.txt) with the format:
```text
[YYYY-MM-DD HH:MM:SS] Username | Pesan: "Original message text" | Label: Classification (Confidence%)
```
