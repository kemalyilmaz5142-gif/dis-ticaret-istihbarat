# Canliya Alma Rehberi

Bu proje iki servis olarak yayinlanir:

1. Backend: FastAPI
2. Frontend: Next.js

## Render ile yayinlama

1. Projeyi GitHub'a yukleyin.
2. Render hesabina girin.
3. `New` > `Blueprint` secin.
4. Bu repoyu secin.
5. Render, kokteki `render.yaml` dosyasini okuyup iki servis olusturur:
   - `dis-ticaret-backend`
   - `dis-ticaret-frontend`

## Dikkat edilmesi gerekenler

- Backend linki olustuktan sonra frontend servisindeki `NEXT_PUBLIC_API_URL` degeri backend linkiyle ayni olmalidir.
- Frontend linki olustuktan sonra backend servisindeki `FRONTEND_ORIGIN` degeri frontend linkiyle ayni olmalidir.
- Ucretsiz servislerde ilk acilis yavas olabilir.
- Ucretsiz servislerde yerel dosya kayitlari kalici olmayabilir. Gercek urun kullaniminda PostgreSQL ve kalici dosya alani baglanmalidir.

## Sunumda soylenecek cumle

Proje localde calisan prototip olarak hazirlandi. Canliya almak icin Docker ve Render blueprint dosyalari eklendi. GitHub'a yuklenip Render'a baglandiginda frontend ve backend ayri servisler olarak yayinlanabilir.
