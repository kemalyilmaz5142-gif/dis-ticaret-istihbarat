# Kaynak Adaptoru Plani

Bu dosya 3. asama icin harita, firma dizini ve dis ticaret veritabani kaynaklarinin nasil baglanacagini tanimlar.

## Ortak Sonuc Formati

Her kaynak `LeadResult` formatina donmelidir:

- `company_name`
- `country`
- `city`
- `address`
- `website`
- `email`
- `phone`
- `source`
- `source_type`
- `matched_keyword`
- `score`
- `notes`

## Harita Kaynaklari

Amac: Web sitesi olmayan ama haritada konumu bulunan firmalari yakalamak.

Baslangic adaptor dosyasi: `apps/backend/app/sources/maps.py`
Canli API adaptor dosyasi: `apps/backend/app/sources/serpapi_maps.py`

Gelecek entegrasyonlar:

- Google Maps Places API
- SerpAPI Local Results
- Apify harita aktorleri
- Yandex Maps uygun ulkeler icin

## Firma Dizinleri

Amac: Firma profili, sektor, web sitesi ve iletisim bilgilerini bulmak.

Gelecek entegrasyonlar:

- Europages
- Kompass
- Thomasnet
- IndiaMART
- Made-in-China
- EC21

## Dis Ticaret Veritabanlari

Amac: Daha hedefli ithalatci/alici verisi yakalamak.

Baslangic adaptor dosyasi: `apps/backend/app/sources/trade_databases.py`

Gelecek entegrasyonlar:

- TradeAtlas
- ImportGenius
- Panjiva
- Trademo Intel
- UN Comtrade
- TradeMap

## Uygulama Notu

Gercek servislerin bir kismi ucretli, uyelikli veya kullanim sartlari kisitli olabilir. Bu nedenle her kaynak icin once izinli API veya resmi veri erisim yontemi tercih edilmeli; otomasyon gerekiyorsa hiz limiti ve hukuki kullanim sinirlari ayrica kontrol edilmelidir.

## Canli Web Arama

Baslangic adaptor dosyasi: `apps/backend/app/sources/web_search.py`

Bu adaptor DuckDuckGo HTML sonuc sayfasindan temel web sonuc bilgisi okumayi dener. Baglanti, hiz limiti veya servis hatasi olursa bos sonuc dondurur ve uygulamanin diger adaptorleri calismaya devam eder.

Ortam ayarlari:

- `ENABLE_LIVE_WEB_SEARCH=true`: Canli web aramayi acar veya kapatir.
- `SERPAPI_API_KEY=`: Doldurulursa SerpAPI Google Maps adaptoru devreye girer.
