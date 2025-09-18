# Images

- `icon.svg` → ikon dasar aplikasi. Untuk packaging macOS, electron-builder idealnya memakai `icon.icns`.
- Kamu bisa konversi dari PNG/SVG ke `.icns` dengan langkah ini:

1) Siapkan `icon.png` berukuran 1024×1024
2) Buat iconset:
mkdir Sertifikita.iconset
sips -z 16 16 icon.png --out Sertifikita.iconset/icon_16x16.png
sips -z 32 32 icon.png --out Sertifikita.iconset/icon_16x16@2x.png
sips -z 32 32 icon.png --out Sertifikita.iconset/icon_32x32.png
sips -z 64 64 icon.png --out Sertifikita.iconset/icon_32x32@2x.png
sips -z 128 128 icon.png --out Sertifikita.iconset/icon_128x128.png
sips -z 256 256 icon.png --out Sertifikita.iconset/icon_128x128@2x.png
sips -z 256 256 icon.png --out Sertifikita.iconset/icon_256x256.png
sips -z 512 512 icon.png --out Sertifikita.iconset/icon_256x256@2x.png
sips -z 512 512 icon.png --out Sertifikita.iconset/icon_512x512.png
cp icon.png Sertifikita.iconset/icon_512x512@2x.png

3) Konversi:
iconutil -c icns Sertifikita.iconset -o icon.icns

4) Pindahkan `icon.icns` ke:
app/resources/images/icon.icns
Electron-builder nanti bisa refer ke ini via config (opsional)
