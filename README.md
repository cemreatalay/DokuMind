# DokuMind 📚

**Yapay Zekâ Destekli Yerel Belge Asistanı**

DokuMind, PDF belgelerindeki bilgileri kullanarak kullanıcıların doğal dilde sorular sormasını sağlayan RAG (Retrieval-Augmented Generation) tabanlı bir belge asistanıdır.

## 🚀 Özellikler

- 📄 PDF belgelerini sisteme ekleme
- 🔎 Anlamsal belge arama
- 🧩 PDF içeriklerini otomatik parçalara ayırma
- 🧠 Embedding ile metinleri vektörlere dönüştürme
- 🗃️ ChromaDB vektör veritabanı
- 🤖 Yerel yapay zekâ modeli ile cevap üretme
- 📚 Kaynak belge ve madde bilgisi gösterme
- 💬 Doğal dil ile soru-cevap
- 🖥️ Streamlit kullanıcı arayüzü
- 🔒 Belgelerin yerel ortamda işlenebilmesi

## 🏗️ Sistem Mimarisi

PDF → PDF Reader → Chunking → Embedding → ChromaDB → Retrieval → Chat Model → Cevap + Kaynak

## 🛠️ Kullanılan Teknolojiler

- Python
- Streamlit
- ChromaDB
- PyMuPDF
- Foundry Local
- Qwen3 Embedding
- Qwen3 1.7B
- RAG

## ▶️ Çalıştırma

```powershell
streamlit run app/web_app.py
```
## 🔍 Örnek

**Soru:** Staj süresi kaç iş günüdür?

**Cevap:** Staj süresi en az 20 iş günüdür.

**Kaynak:** Madde 3 - test.pdf

## 🎯 Projenin Amacı

DokuMind, uzun PDF belgeleri içerisindeki bilgilere doğal dil kullanarak hızlı ve kaynak göstererek ulaşmayı amaçlamaktadır.

## 👩‍💻 Geliştirici

**Cemre Atalay**

GitHub: https://github.com/cemreatalay

