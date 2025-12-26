# Yükleme Planı Formu → PDF (Flask + ReportLab)

Bu mini uygulama; **MÜŞTERİ ADI / SIRA NO / ÜRÜN TİPİ / SAAT VE TARİH** alanlarını bir web formundan alır ve tek sayfalık PDF üretip indirir.

## Kurulum
```bash
cd app
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
python app.py
```

Tarayıcıdan aç:
- http://localhost:5000

## Üretim notları (kısa)
- İnternete açık yayınlayacaksanız `debug=False` kullanın.
- İsterseniz logo / firma bilgisi / ek alanlar / imza alanı ekleyebilirim.
