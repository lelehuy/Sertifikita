# Sertifikita

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey)
![Downloads](https://img.shields.io/github/downloads/lelehuy/Sertifikita/total)

**Sertifikita** adalah aplikasi desktop modern dan ringan untuk mendesain serta membuat sertifikat secara massal (*batch*) dengan cepat dan mudah.

---

## ✨ Fitur Utama

- 🖼️ **Template-based**: Gunakan gambar PNG/JPG/WEBP apa pun sebagai latar belakang sertifikat Anda.
- 🔤 **Dynamic Text Fields**: Tambahkan kolom teks dinamis yang bisa digeser (*drag*), diubah ukurannya (*resize*), dan diatur perataannya (*left/center/right*).
- 🧭 **Live Canvas**: Lihat perubahan secara langsung, lengkap dengan fitur *Snap 5px* untuk presisi dan dukungan *Zoom* (CTRL + Scroll).
- 📁 **Drag & Drop**: Tarik file gambar template atau file CSV langsung ke aplikasi untuk impor instan.
- 🗂️ **Manage Data**: Kelola data penerima langsung di tabel aplikasi atau impor/ekspor via CSV.
- 🧩 **Custom Filename**: Gunakan pola nama file dinamis seperti `{row}-{Nama}-{Kursus}`.
- 👀 **Preview Modern**: Pratinjau hasil desain dengan satu klik sebelum melakukan ekspor masal.
- 🖨️ **Batch Generate**: Ekspor semua sertifikat sekaligus ke format **PNG** atau **PDF** berkualitas tinggi.

---

## 🖥️ Cara Instalasi (macOS)

1. Unduh file **`Sertifikita-<versi>-arm64.dmg`** dari menu [Releases](https://github.com/lelehuy/Sertifikita/releases).
2. Buka file DMG dan tarik ikon **Sertifikita** ke folder **Applications**.
3. **Penting**: Saat pertama kali menjalankan aplikasi, klik kanan pada ikon aplikasi dan pilih **Open** untuk melewati verifikasi keamanan macOS (Gatekeeper).

---

## ⌨️ Shortcut Keyboard

- `Ctrl + O`: Buka Template Gambar
- `Ctrl + S`: Simpan Konfigurasi Field (JSON)
- `Ctrl + G`: Mulai Generate Sertifikat
- `Delete / Backspace`: Hapus elemen teks yang dipilih
- `Ctrl + Scroll`: Zoom In / Out pada kanvas

---

## 📄 Format CSV

- **Impor**: Baris pertama harus berupa header kolom. Kolom harus sesuai dengan nama label yang Anda buat di kanvas (misal: `Nama`, `Kursus`).
- **Ekspor**: Anda bisa mengekspor data tabel yang ada kembali ke format CSV.

---

## 🧑‍💻 Untuk Pengembang (Developers)

Jika Anda ingin berkontribusi atau menjalankan aplikasi dari kode sumber, silakan baca panduan di:
👉 **[development.md](./development.md)**

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah **GPL v3 License**.
