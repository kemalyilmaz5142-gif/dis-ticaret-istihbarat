# Dis Ticaret Istihbarat Platformu

Bu proje, verilen yazilim recetesine gore potansiyel yurt disi musterileri bulmak, web sitesi ziyaretcilerini analiz etmek, arama/harita/veritabani kaynaklarini taramak ve sonuclari Excel olarak cikarmak icin tasarlanmistir.

## 5 Asamali Yol Haritasi

1. **MVP temel iskelet**
   - Next.js + TypeScript web arayuzu
   - FastAPI backend
   - PostgreSQL baglanti ayarlari
   - Musteri arama formu
   - Excel cikti servisi
   - Moduler klasor yapisi

2. **Potansiyel musteri arama motoru**
   - Ulke, dil, urun adi, GTIP, OEM ve rakip bilgisine gore arama gorevleri
   - Playwright ile arama motoru otomasyonu
   - Valentin benzeri lokasyon simule eden servis/masaustu arac entegrasyon noktasi
   - Sonuc temizleme, tekillestirme ve puanlama

3. **Harita ve firma verisi toplama**
   - Harita uzerinden firma arama
   - Web sitesi, telefon, e-posta, adres ve sektor bilgisi toplama
   - Tradeatlas, Europages, Kompass, UN Comtrade gibi kaynaklar icin adaptor mimarisi

4. **AI zenginlestirme ve iletisim**
   - Urun adi ceviri/dogrulama
   - IATE/Cambridge benzeri sozluk dogrulama katmani
   - Web sitesinden ilgili kisi/e-posta tahmini
   - Otomatik tanitim maili taslaklari ve spam risk kontrolu

5. **Ticari paketleme ve ek moduller**
   - Kullanici/abonelik/modul yetkilendirme
   - Ziyaretci firma tespiti
   - Web chat robotu
   - Fuar katilimci tarama
   - Cin ve ABD odakli ozel arama modulleri

## Proje Yapisi

```text
apps/
  backend/     FastAPI servisi
  frontend/    Next.js + TypeScript arayuzu
automation/    Playwright otomasyonlari
ai/            AI destekli zenginlestirme servisleri
docs/          Urun ve asama dokumanlari
```

## 1. Asama Durumu

Bu asamada temel gelistirme iskeleti kuruldu. Backend tarafinda saglik kontrolu, arama talebi alma, ziyaretci izni kaydetme ve Excel cikti ucu hazirlandi. Frontend tarafinda giris ekrani, arama formu ve sonuc tablosu baslangic deneyimi eklendi.

## Projeyi Baslatma

Kok klasorde su dosyayi calistirin:

```bash
python main.py
```

Ilk calistirmada backend ve frontend paketleri kurulmaya calisilir. Sonrasinda backend `http://localhost:8000` adresinde acilir. Frontend uygun olan ilk portta acilir; genelde `http://localhost:3000`, doluysa `3001`, `3002` gibi devam eder.

Projeyi kapatmak icin:

```bash
python stop.py
```
