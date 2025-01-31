# **KRNL Twitter Bot - RAG-Enhanced with Llama**

This repository contains a **Twitter bot** built with:
1. **Tweepy (Twitter API v2)**  
2. **FAISS for retrieval-augmented generation (RAG)**  
3. A **quantized Llama model** (e.g., `meta-llama/Llama-3.1-7B-Instruct`) using **BitsAndBytes** for efficient GPU memory usage  

The bot can:
- **Post tweets** at random intervals or on command  
- **Reply** to user mentions up to 4 times each  
- **Integrate knowledge** from your **FAISS** index (loaded from `.txt` documents about KRNL or your company), **but only if relevant**  
- **Embody** a comedic, self-deprecating, “degen,” KRNL-loyal intern persona

---

## **Table of Contents**
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Directory Structure](#directory-structure)  
4. [Installation](#installation)  
5. [Setup & Configuration](#setup--configuration)  
6. [Usage](#usage)  
7. [Detailed Flow](#detailed-flow)  
8. [Customization](#customization)  
9. [Notes & Caveats](#notes--caveats)  
10. [License](#license)

---

## **Project Overview**

1. **Core Bot**: Uses **Tweepy** `Client` for **Twitter API v2**. Posts new tweets, replies to mentions, and abides by a per-user reply limit.  
2. **LLM Integration**: A **Llama** model is loaded via Hugging Face’s `transformers` with 8-bit quantization (`bitsandbytes`).  
3. **RAG (Retrieval-Augmented Generation)**: A **FAISS** index is built from your `.txt` files containing knowledge about KRNL or your company. The bot **always** retrieves top-k chunks for any query or tweet topic and includes them in the prompt, telling the LLM to “use if relevant, ignore if not.”  

As a result, the **LLM** can self-decide whether to incorporate your internal/company knowledge into the tweet or reply.

---

## **Features**

- **Quantized Model**: Loads a 7B Llama Instruct model in 8-bit, lowering VRAM usage.  
- **Twitter API v2**: Posts tweets and replies at scale with rate-limit handling.  
- **RAG** via FAISS**: Index your `.txt` data; the model references it for relevant queries.  
- **Persona**: Self-deprecating, comedic style, “intern-turning-CEO,” loyal to KRNL.  
- **Random Topics**: Merges random topics from `topics.txt` with hypothetical “personalized trends.”  
- **Reply Limits**: Up to 4 replies per user (tracked in `user_interactions.json`).

---

## **Directory Structure**
twitter-bot/
├── bot.py                 # Main logic for tweeting/replying
├── config.py              # Twitter credentials & settings
├── llm_utils.py           # Model initialization & RAG-based generation
├── rag_utils.py           # FAISS index building & context retrieval
├── scheduler.py           # Scheduling logic for posting & replies
├── topics.txt             # List of random topics for tweet generation
├── personalized_trends.txt# (Optional) file for custom "trends" data
├── user_interactions.json # Tracks how many times each user has been replied to
├── company_data/          # Folder with .txt files about your company
│   └── about_company.txt  # Example .txt for indexing
├── logs/
│   └── bot.log            # Logging output
└── requirements.txt       # Dependencies


## **Setup & Configuration**

1. **Twitter API Credentials**  
   - Create a Twitter Developer account.  
   - In `config.py` (or as environment variables), set:
     ```python
     BEARER_TOKEN = "YOUR_BEARER_TOKEN"
     V2_CLIENT_ID = "YOUR_CLIENT_ID"
     V2_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
     V2_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
     V2_ACCESS_SECRET = "YOUR_ACCESS_SECRET"
     ```

2. **Model & FAISS**  
   - In `rag_utils.py`, confirm your **FAISS** index is built from the `.txt` files in `company_data/`.  
   - In `llm_utils.py`, ensure `init_model()` references the correct Llama model.

3. **topics.txt**  
   - Add lines of random topics you’d like the bot to tweet about.

4. **(Optional) personalized_trends.txt**  
   - Populate automatically if you have a custom `/2/users/personalized_trends` endpoint, or manually by writing lines of text.

5. **user_interactions.json**  
   - Auto-created if missing. Tracks per-user reply counts.

---

## **Usage**

### **1. Initial Steps**
- **Initialize** the FAISS index (automatically done in `bot.py` via `initialize_faiss_index()`).
- **Initialize** the LLM by calling `init_model()`.

### **2. Run Locally**
```bash
python3 bot.py
```

or Run:
```bash
python3 scheduler.py
```
