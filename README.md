# Loading Plan -> PDF (TR Font Supported)

Bu mini Flask uygulaması; formdan **Müşteri Adı / Sıra No / Ürün Tipi / Saat ve Tarih** alır ve PDF üretip indirir.

## Çalıştırma (lokal)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Sonra tarayıcıdan: http://localhost:5000

## Türkçe karakter desteği
PDF için DejaVu fontları `fonts/` klasöründedir ve ReportLab'e register edilmiştir.
