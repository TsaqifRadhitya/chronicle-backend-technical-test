# Chronicle Backend Technical Test

Repository ini berisi solusi Backend Technical Test untuk aplikasi E-Commerce sederhana. Proyek ini dibangun menggunakan Django Rest Framework (DRF) dan dioptimalkan dengan PostgreSQL, Redis, dan Celery.

## Instruksi Instalasi & Setup (Menggunakan Docker)

Proyek ini telah dikonfigurasi menggunakan Docker untuk memudahkan proses *deployment* dan pengembangan. Ikuti langkah-langkah berikut untuk menjalankan aplikasi:

1.  **Clone Repository**
    ```bash
    git clone <repository_url>
    cd chronicle-backend-technical-test
    ```

2.  **Konfigurasi Environment Variables**
    Salin file contoh environment menjadi file `.env`. File ini berisi konfigurasi untuk database dan Redis.
    ```bash
    cp .env.example .env
    ```

3.  **Jalankan Aplikasi**
    Gunakan Docker Compose untuk membangun dan menjalankan seluruh layanan (Web, Database, Redis, Celery).
    ```bash
    docker-compose up --build
    ```

    **Catatan Otomatisasi:**
    * Perintah ini akan secara otomatis menjalankan migrasi database dan seeder.
    * Server akan dapat diakses di `http://localhost:8000`.

4.  **Menghentikan Aplikasi**
    Untuk menghentikan server, tekan `Ctrl+C` atau jalankan perintah:
    ```bash
    docker-compose down
    ```

## Dokumentasi API

Dokumentasi lengkap mengenai endpoint API beserta contoh request dan response dapat diakses melalui Postman Collection berikut:

[**🔗 Link ke Postman Collection**]

*https://tsaqif-4124259.postman.co/workspace/Tsaqif's-Workspace~404253c0-b3b2-4378-80bc-a7d7f03279f9/collection/44671713-f2c2f00d-4a59-421d-a5f7-7ec2f95610ce?action=share&creator=44671713&active-environment=44671713-e5c924ed-4861-40fa-8c37-93e44e22fc0d*


## Penanganan Race Condition (Stock Management)

Salah satu fitur kunci dalam sistem ini adalah pencegahan *overselling* ketika terjadi banyak permintaan pemesanan secara bersamaan (*concurrent requests*).

### Mekanisme: Locking Row (Pessimistic Locking)

Untuk menangani *race condition*, sistem menggunakan pendekatan **Row-Level Locking** pada database.

**Cara Kerja:**
1.  Saat sebuah request (transaksi) mencoba mengubah stok produk (misalnya saat membuat Order baru), sistem akan mengunci baris data (*row*) produk tersebut menggunakan `select_for_update()` di dalam blok transaksi atomik (`transaction.atomic`).
2.  Karena baris data tersebut dikunci, request lain yang mencoba mengakses atau mengubah baris data produk yang sama **harus menunggu** hingga transaksi pertama selesai dan kunci (*lock*) dilepaskan.
3.  Hal ini memastikan bahwa pengecekan stok (`if product.stock < quantity`) selalu akurat dan konsisten, serta mencegah stok menjadi negatif akibat modifikasi data yang tumpang tindih.