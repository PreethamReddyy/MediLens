# MediLens 🩺🔍

## AI-Powered Multilingual Prescription Understanding & Medication Assistant

![MediLens Banner](assets/banner.png)

## 📌 Overview

**MediLens** is an AI-powered healthcare assistance system designed to help elderly people, visually impaired users, and individuals who struggle with reading medicine labels or handwritten prescriptions.

The system uses **Computer Vision, OCR, Natural Language Processing, and Text-to-Speech** technologies to understand medicine information, explain it in simple language, and assist users with medication management.

MediLens aims to reduce medication errors by making prescriptions easier to understand through AI-powered assistance.

---

# 🎯 Problem Statement

Many people face difficulties with:

* Reading small medicine labels
* Understanding handwritten doctor prescriptions
* Remembering medicine timings
* Understanding medicine usage information
* Accessing healthcare information in their native language

These problems are especially common among elderly people and users with vision difficulties.

---

# 💡 Solution

MediLens provides an intelligent assistant that can:

📷 Scan medicine strips and prescriptions
🔍 Extract medicine information using OCR
💊 Identify medicines from a database
🔊 Read medicine details aloud in multiple languages
⏰ Create medicine reminders
🛒 Provide online medicine search links
📄 Generate simple prescription summaries

---

# ✨ Features

## 1. Medicine & Prescription Scanner

* Upload an image of a medicine strip or prescription
* Enhance image quality using computer vision techniques
* Extract text using OCR

Supported inputs:

* Printed medicine labels
* Prescription images
* Medicine packaging

---

## 2. AI-Based Medicine Recognition

The extracted text is processed to identify:

* Medicine name
* Generic name
* Strength
* Basic information

Uses fuzzy matching to handle OCR mistakes.

Example:

```
OCR Output:
Paracetmol 650

Matched:
Paracetamol 650mg
```

---

## 3. Medicine Information

Provides:

* Common uses
* General information
* Common side effects
* Precautions

Note:
MediLens provides educational information and does not replace professional medical advice.

---

## 4. Multilingual Voice Assistant

MediLens can read medicine information aloud.

Supported languages:

* English
* Hindi
* Telugu

Example:

> "Take one tablet after food twice daily."

---

## 5. Smart Dosage Parser

Converts normal dosage instructions into structured information.

Example:

Input:

```
Take one tablet twice daily after food for 5 days
```

Output:

```
Morning:
1 tablet

Night:
1 tablet

Duration:
5 days
```

---

## 6. Medicine Reminder System

Creates medication schedules based on dosage instructions.

Features:

* Reminder timings
* Medication tracking
* Taken/Missed status

---

## 7. Online Medicine Search

After detecting medicine names, MediLens provides quick search options for online availability.

---

# 🏗 System Architecture

```
User Image

     ↓

Image Preprocessing

     ↓

OCR Engine

     ↓

Medicine Name Extraction

     ↓

Medicine Database

     ↓

AI Processing Layer

     ↓

 ┌───────────────┐
 │               │
 ▼               ▼

Voice Output   Reminder System

     ↓

User Interface
```

---

# 🛠 Tech Stack

## Programming Language

* Python

## Computer Vision

* OpenCV
* Pillow
* NumPy

## OCR

* EasyOCR
* PaddleOCR / Transformer OCR (Future)

## NLP

* Natural Language Processing
* Fuzzy String Matching

## Database

* SQLite
* PostgreSQL (Future)

## Frontend

* Streamlit

## AI/ML

* Hugging Face Transformers
* Sentence Transformers

## Deployment

* Docker
* Cloud Deployment (Future)

---

# 📂 Project Structure

```
MediLens/

│
├── app/
│   ├── main.py
│   ├── preprocessing/
│   ├── ocr/
│   ├── database/
│   ├── parser/
│   ├── voice/
│   ├── reminder/
│   └── utils/
│
├── data/
│   ├── samples/
│   └── medicine_database/
│
├── models/
│
├── notebooks/
│
├── tests/
│
├── assets/
│
├── requirements.txt
│
├── README.md
│
└── .gitignore
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/medilens.git
```

## Navigate to Project

```bash
cd medilens
```

## Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

```bash
streamlit run app/main.py
```

---

# 📌 Development Roadmap

## Phase 1 - Foundation

✅ Project setup
✅ Git workflow
✅ Basic architecture

## Phase 2 - OCR Pipeline

⬜ Image preprocessing
⬜ Medicine text extraction
⬜ OCR improvement

## Phase 3 - Medicine Intelligence

⬜ Medicine database
⬜ Fuzzy matching
⬜ Information retrieval

## Phase 4 - User Assistance

⬜ Voice output
⬜ Dosage parser
⬜ Reminder system

## Phase 5 - Advanced Features

⬜ Handwritten prescription improvement
⬜ Drug interaction warnings
⬜ AI chatbot using RAG
⬜ Mobile application

---

# 🔒 Safety Considerations

MediLens is designed as an assistance tool.

It does not:

* Diagnose diseases
* Replace doctors
* Recommend changing medication
* Provide personalized medical decisions

Users should always verify medical information with qualified healthcare professionals.

---

# 👨‍💻 Developer

Built as an AI/ML project focusing on:

* Computer Vision
* Natural Language Processing
* Healthcare Technology
* Responsible AI

---

# ⭐ Future Vision

MediLens aims to become an accessible healthcare companion that helps people better understand their medications through artificial intelligence and local language support.

---

## License

This project is for educational and research purposes.
