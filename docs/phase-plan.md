# 5 Asamali Uygulama Plani

## Asama 1: MVP Temel Iskelet

Amac: Urunun calisabilir ilk govdesini kurmak.

- Kullanici girisi icin sade ekran
- Potansiyel musteri arama formu
- Ulke, dil, urun, GTIP, OEM, rakip ve sektor alanlari
- FastAPI ile arama gorevi olusturma
- PostgreSQL icin ortam ayarlari
- Excel cikti servisi
- Otomasyon ve AI klasorlerinin baglanti noktalarini hazirlama

Basari kriteri: Kullanici formu doldurur, backend arama istegini alir, ornek sonuclar doner ve Excel olarak indirilebilir.

## Asama 2: Arama Otomasyonu

Amac: Arama motorlari ve ulke/lokasyon bazli tarama akisini kurmak.

- Playwright ile Google/Yandex/Bing arama adaptorleri
- Ulke uzantisi ve hedef dil destegi
- Valentin benzeri lokasyon simule eden katman
- Rakip marka ve bagli sektor/GTIP sorgulari
- Sonuc skorlama ve tekillestirme

## Asama 3: Harita ve Veritabani Kaynaklari

Amac: Web sitesi olmayan firmalari ve dis ticaret verilerini yakalamak.

- Harita firma arama adaptorleri
- Firma iletisim bilgisi cikarma
- Tradeatlas, ImportGenius, Panjiva, Europages, Kompass vb. kaynaklar icin adaptor altyapisi
- Excel kolon standardi

Durum: Baslangic adaptor mimarisi eklendi. Harita, firma dizini ve dis ticaret veritabani kaynaklari ortak `LeadResult` formatina donusturuluyor. Gercek API/uyelik bilgileri geldiginde adaptorlerin icindeki ornek veri uretimi canli veri toplama ile degistirilecek.

## Asama 4: AI Zenginlestirme ve Iletisim

Amac: Bulunan firmalari anlamlandirmak ve iletisime hazir hale getirmek.

- Urun adi ceviri ve sozluk dogrulama
- Firma uygunluk puani
- Yetkili e-posta tahmini
- Tanitim maili taslagi
- Spam risk azaltma kurallari

Durum: Ilk AI zenginlestirme katmani eklendi. Sonuclar icin uygunluk nedeni, onerilen kontak rolu, mail konusu ve mail govdesi uretiliyor. Bu katman su an kural tabanli; ileride LLM veya ceviri/sozluk API servisleriyle guclendirilecek.

## Asama 5: Paketleme ve Ek Moduller

Amac: Urunu satis yapilabilir, moduler ve kontrol edilebilir hale getirmek.

- Kullanici, abonelik, modul yetkileri
- Ziyaretci firma tespiti
- Chat robotu
- Fuar katilimci tarama
- Cin/ABD ozel arama paketleri

Durum: Ilk modul katalogu, demo abonelik plani ve modul erisim kontrolu eklendi. Backend `lead_search` modul erisim kontrolunu arama akisi oncesinde calistiriyor. Bu yapi ileride PostgreSQL tabanli musteri, abonelik, kullanim limiti ve faturalandirma tablolarina tasinacak.

Guncelleme: Demo abonelik kullanim sayaci eklendi. `GET /api/subscription` artik kalici demo kullanim sayisini dondurur; basarili her potansiyel musteri aramasindan sonra sorgu sayaci artar. `POST /api/subscription/reset-usage` demo/test icin sayaci sifirlar. PostgreSQL yoksa sayac JSON dosyasi ile korunur.

### Cin/ABD Ozel Arama Paketleri

Durum: Ilk pazar stratejisi katmani eklendi. Arama formuna `Standart`, `Cin pazari` ve `ABD pazari` secimi eklendi. Backend bu secime gore arama sorgularina pazar odakli niyet kelimeleri, kaynak ipuclari ve domain varsayilanlari ekler. Bu yapi ileride Cin kaynak platformlari, ABD distributor veritabanlari ve ulkeye ozel API adaptorleriyle genisletilecek.

### Fuar Katilimci Tarama

Durum: Ilk fuar tarama akisi eklendi. `POST /api/fairs/scan` fuar adi, ulke, urun, sektor ve fuar web sitesi bilgisine gore katilimci adaylari uretir. Frontend uzerinde ayri panelden tarama yapilir ve `POST /api/exports/fair-participants.xlsx` ile Excel ciktisi alinabilir. Su an kural tabanli demo veri uretilir; gercek fuar web sitesi/katilimci listesi parse etme adaptoru sonraki entegrasyonda baglanacak.

### Web Chat Robotu

Durum: Ilk yardimci chat akisi eklendi. `POST /api/chat/answer` kullanici sorusunu ve mevcut arama sonuclarini alir; firma onceliklendirme, Excel cikti, mail kampanyasi ve fuar tarama konularinda kural tabanli cevap ve aksiyon onerileri uretir. Bu katman ileride LLM tabanli Python AI servisine baglanacak sekilde ayrildi.

### Web Ziyaretci Tespiti Modulu

Durum: Ilk ziyaretci izin akisi eklendi. Frontend uzerinden ziyaretciye konum izni soruluyor; evet durumunda koordinatlar, hayir durumunda IP takip adimi kaydediliyor. Backend `POST /api/visitors/consent` ve `GET /api/visitors` uclarini sagliyor. Firma tahmini su an kural tabanli yer tutucu olarak calisir; IP/firma eslestirme servisi baglaninca canli firma adi donecek.

Guncelleme: IP lookup katmani eklendi. `IPINFO_TOKEN` varsa ipinfo kullanilir; yoksa temel `ip-api` denemesi yapilir. Localhost/ozel IP adreslerinde dis servise cikmadan yerel tahmin uretilir.

### Urun Resmiyle Arama

Durum: Ilk gorsel yukleme ve imza uretme akisi eklendi. Frontend urun resmi secimini kabul eder, backend `POST /api/images/product` ile dosyayi kaydeder ve SHA256 imzasi uretir. Arama istegine `product_image_id` eklenirse `image_search` kaynagi devreye girer. Gercek tersine gorsel arama veya goruntu benzerligi servisi bu adaptore baglanacak.

### Yetkili E-posta Bulma

Durum: Ilk kural tabanli kontak tahmin katmani eklendi. Firma web sitesi veya e-posta domaininden `purchasing@`, `procurement@`, `import@`, `buyer@`, `sales@`, `manager@` gibi adaylar uretiliyor. Excel ciktisina ve frontend sonuc tablosuna bu adaylar ekleniyor. Gercek web sitesi iletisim sayfasi tarama ve kisi bazli e-posta dogrulama sonraki entegrasyonda eklenecek.

### Otomatik Mail Gonderme Hazirligi

Durum: Guvenli kampanya onizleme katmani eklendi. `POST /api/campaigns/preview` arama sonuclarindan alici adaylari, mail konusu, mail govdesi ve spam-risk uyarilari uretir. Gercek SMTP/toplu gonderim henuz yapilmaz; once onizleme ve risk kontrolu yapilir.

Guncelleme: Kampanya kuyrugu eklendi. `POST /api/campaigns/queue` onizlenen kampanyayi kalici kuyruga alir, `GET /api/campaigns` son kampanyalari listeler. SMTP ayarlari `.env` ile hazirlandi ancak `ENABLE_EMAIL_SENDING=false` oldugu surece gercek mail gonderimi kapali kalir. Bu, satis oncesi demo ve test kullanimi icin guvenli varsayilandir.

## Asama 6: Kalici Veri ve Operasyon Hazirligi

Amac: Prototipi kullanici islemlerini kaydeden, takip edilebilir ve operasyona hazir bir uygulamaya yaklastirmak.

- Arama ve sonuc tablolarinin genisletilmesi
- Arama gecmisi API ucu
- Frontend gecmis aramalar paneli
- PostgreSQL baglantisi yoksa uygulamanin arama akisini bozmadan devam etmesi
- Musteri profil ayarlari
- Kullanim limiti ve demo abonelik takibi
- Sistem/entegrasyon durum paneli
- Operasyon raporu Excel ciktisi

Durum: Arama kaydi ve lead sonuc modelleri eklendi. `GET /api/searches/history` ucu hazirlandi. PostgreSQL baglantisi hazir oldugunda arama gecmisi otomatik dolacak.

Guncelleme: Musteri profil ayarlari eklendi. `GET /api/customer/profile` ve `POST /api/customer/profile` uclari musteri adi, sirket adi, web sitesi, katalog linki, gonderici e-posta ve hedef sektor bilgisini kalici olarak saklar. Frontend profil paneli bu bilgileri yonetir; mail kampanyasi onizlemesi sirket adi ve katalog linkini artik bu profilden alir.

Guncelleme: Sistem durum paneli eklendi. `GET /api/system/status` PostgreSQL, canli web arama, SerpAPI, IP lookup, SMTP ve JSON yedek kayit durumlarini raporlar. Frontend bu bilgileri entegrasyon hazirligi panelinde gosterir.

Guncelleme: Operasyon raporu Excel ciktisi eklendi. `GET /api/exports/operation-report.xlsx` musteri profili, abonelik ozeti, entegrasyon durumu, modul katalogu, arama gecmisi ve kampanya kuyrugunu cok sayfali Excel dosyasi olarak uretir.

## Word Dosyasina Gore Sirali Eksikler

### 1. Giris Ekrani ve Kullanici Sifre Kontrolu

Durum: Ilk demo giris akisi eklendi. `POST /api/auth/login` demo kullanici adi ve sifreyi kontrol eder. Frontend artik giris yapilmadan ana paneli gostermez; basarili oturum tarayicida saklanir ve ust panelden cikis yapilabilir. Varsayilan demo bilgiler `.env.example` icinde `DEMO_USERNAME=demo` ve `DEMO_PASSWORD=demo123` olarak tanimlandi. Bu katman ileride PostgreSQL tabanli cok kullanicili hesap, rol ve lisans kontrolune tasinacak.

### 2. Valentin Benzeri Lokasyon Simulasyonu

Durum: Ilk lokasyon simulasyonu planlama katmani eklendi. Arama formuna lokasyon saglayici secimi ve hedef ulkeden araniyormus gibi planlama kutusu eklendi. Backend `simulate_search_location` ve `location_provider` alanlarini arama planina tasir; sorgulara hedef ulke lokasyon ipucu ekler ve sonuclara simulasyon notu isler. Sistem durum paneli `ENABLE_LOCATION_SIMULATION`, `LOCATION_PROVIDER` ve `VALENTIN_APP_PATH` ayarlarina gore lokasyon simulasyonu hazirligini raporlar. Gercek Valentin masaustu otomasyonu veya Playwright geo baglayicisi sonraki adimda bu katmana takilacak.

### 3. Coklu Arama Motoru Adaptoru

Durum: Arama planina Google, Bing, Yandex ve Safari/Web secimi eklendi. Frontend formunda arama motorlari secilebilir hale geldi. Backend `search_engines` alanini okuyarak her motor icin ayri sorgu planlari uretir ve canli web adaptoru sonucu planlanan motor etiketiyle isaretler. Gercek motor API'leri veya Playwright tarayici otomasyonlari sonraki entegrasyonda bu planlara baglanacak.

### 4. IATE ve Cambridge Sozluk Dogrulama

Durum: Ilk sozluk dogrulama katmani eklendi. `POST /api/ai/dictionary/validate` serbest terimleri, `POST /api/ai/dictionary/from-search` ise arama formundaki urun adlarini dogrulama raporuna cevirir. Su an yerel sozluk ve `IATE-ready` / `Cambridge-ready` kaynak etiketleri kullanilir; gercek IATE/Cambridge API veya scraping entegrasyonu bu servisin icine baglanacak.

### 5. Tum Diller ve Tum Ulkeler Toplu Arama

Durum: Ilk toplu arama planlama modu eklendi. Arama istegi artik `extra_language_terms`, `search_all_countries`, `country_groups` ve `extra_target_countries` alanlarini destekler. Frontend uzerinde Avrupa, Orta Dogu, Turk Cumhuriyetleri, Amerika ve Asya ulke paketleri secilebilir; ek ulkeler ve ek dil terimleri girilebilir. Backend secilen ulke paketlerine gore kontrollu sayida sorgu plani uretir.

### 6. Tersine Gorsel Arama ve Goruntu Isleme

Durum: Gorsel yukleme katmani guclendirildi. Urun resmi kaydedilirken SHA256 imzasina ek olarak opsiyonel Pillow analiziyle genislik, yukseklik, format, ortalama renk ve basit gorsel imza uretilir. `image_search` adaptoru artik bu gorsel imzayi sonuc notlarina ve aday URL'lerine tasir. Gercek tersine gorsel arama API'si veya vektor benzerlik indeksi sonraki entegrasyonda bu metadatalari kullanacak.

### 7. Dis Ticaret Veritabani Entegrasyonlari

Durum: Dis ticaret kaynak katalogu eklendi. TradeAtlas, ImportGenius, Trademo Intel, Panjiva, Global Buyers Online, Europages, TradeKey, TradeMap, Oneworld Yellow Pages, Vujis, Apify, Exim Data, TradecalculusAI, UN Comtrade ve Kompass kaynaklari durum servisinde ve arama formunda secilebilir hale geldi. `ENABLED_TRADE_SOURCES` ayari ile canliya hazir kaynaklar isaretlenebilir; uyelik/API bilgisi geldikce mevcut adaptore baglanacak.

### 8. B2B Talep Avi / RFQ Modulu

Durum: Ilk RFQ tarama katmani eklendi. `POST /api/rfq/scan` urun, hedef ulke, GTIP ve secilen platformlara gore talep adaylari uretir. Frontend'de B2B talep avi paneli eklendi. TradeKey, ECPlaza, eWorldTrade, IndiaMART, TradeIndia, Made-in-China, DHgate, EC21 ve Thomasnet platformlari secilebilir. Simdilik demo adaylar uretilir; canli RFQ/uyelik/API entegrasyonu sonraki adimda baglanacak.

### 9. Otomatik Talep Paylasimi

Durum: Ilk talep paylasimi kuyrugu eklendi. `POST /api/demand-shares` urun, hedef pazarlar, mesaj ve kanal bilgisiyle paylasim taslagini kuyruga alir; `GET /api/demand-shares` son kayitlari listeler. Frontend'de otomatik talep paylasimi paneli eklendi. Guvenli demo modunda dis platformlara otomatik yayin yapilmaz; kayitlar once manuel onaya duser.

### 10. Dis Ticaret Egitim Modulu

Durum: Ilk egitim takip katmani eklendi. `GET /api/training/lessons` dersleri listeler, `POST /api/training/quiz` personel quiz sonucunu kaydeder, `GET /api/training/results` son egitim sonuclarini getirir. Frontend'de dis ticaret egitim paneli eklendi. Bu yapi ileride video ders, anlik soru, fraud onleme ve personel tamamlama raporlarina genisletilecek.

### 11. Siteye Gomulebilir Chat Widget

Durum: Ilk gomulebilir chat widget katmani eklendi. `POST /api/widget/message` ziyaretci mesajini, e-posta ve telefon bilgisini lead kaydi olarak saklar; `GET /api/widget/leads` son kayitlari listeler. Frontend'de widget kodu ve gelen lead kayitlari icin ayri panel eklendi. `apps/frontend/public/chat-widget.js` dosyasi musteri sitesine script olarak eklenebilecek sekilde hazirlandi.

### 12. Fuar Katilimci Listesi ve Web Sitesi Link Taramasi

Durum: Fuar katilimci tarama akisi liste/link girdisiyle genisletildi. `POST /api/fairs/list-scan` katilimci firma adlarini ve web sitesi linklerini hedef urun/sektor bilgisine gore puanlar. Frontend'de katilimci adlari ve web sitesi linkleri yapistirilabilen ikinci fuar tarama paneli eklendi. Bu yapi gercek fuar sayfasi parse etme veya Playwright tabanli link tarama otomasyonuna baglanmaya hazir.
