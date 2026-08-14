# Ticari Paketleme ve Modul Yapisi

5. asama ile uygulama modul bazli paketlenmeye hazirlandi.

## Hazir Backend Uclari

- `GET /api/modules`: Modul katalogunu dondurur.
- `GET /api/subscription`: Demo musteri abonelik planini dondurur.
- `POST /api/access/check`: Bir modul icin erisim kontrolu yapar.
- `POST /api/searches`: `lead_search` modul yetkisi varsa arama akisini calistirir.

## Ilk Modul Katalogu

- `lead_search`: Potansiyel Musteri Arama
- `maps_search`: Harita Firma Arama
- `contact_finder`: Yetkili E-posta Bulma
- `email_outreach`: Otomatik Mail Gonderimi
- `fair_scan`: Fuar Katilimci Tarama
- `visitor_identification`: Web Ziyaretci Tespiti

## Sonraki Ticari Adimlar

1. Musteri ve kullanici tablolari PostgreSQL'e alinacak.
2. Modul erisimleri musteri aboneligine baglanacak.
3. Aylik sorgu limitleri gercek kullanimla artacak.
4. Modul bazli fiyatlar yonetim panelinden degistirilecek.
5. Odeme/faturalandirma sistemi eklenecek.

