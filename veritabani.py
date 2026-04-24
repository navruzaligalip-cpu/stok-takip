"""SQLite veritabanı bağlantı ve tablo yönetimi."""
import sqlite3
import os
from contextlib import contextmanager

VERITABANI_DOSYASI = "stok.db"


def baglanti_olustur() -> sqlite3.Connection:
    baglanti = sqlite3.connect(VERITABANI_DOSYASI)
    baglanti.row_factory = sqlite3.Row
    baglanti.execute("PRAGMA foreign_keys = ON")
    return baglanti


@contextmanager
def veritabani():
    baglanti = baglanti_olustur()
    try:
        yield baglanti
        baglanti.commit()
    except Exception:
        baglanti.rollback()
        raise
    finally:
        baglanti.close()


def tablolari_olustur():
    with veritabani() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS kategoriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL UNIQUE,
                aciklama TEXT,
                olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tedarikciler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                telefon TEXT,
                eposta TEXT,
                adres TEXT,
                vergi_no TEXT,
                olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kod TEXT NOT NULL UNIQUE,
                ad TEXT NOT NULL,
                kategori_id INTEGER,
                tedarikci_id INTEGER,
                barkod TEXT UNIQUE,
                birim TEXT NOT NULL DEFAULT 'adet',
                alis_fiyati REAL NOT NULL DEFAULT 0,
                satis_fiyati REAL NOT NULL DEFAULT 0,
                kdv_orani REAL NOT NULL DEFAULT 18,
                stok_miktari REAL NOT NULL DEFAULT 0,
                minimum_stok REAL NOT NULL DEFAULT 5,
                maksimum_stok REAL,
                raf_konumu TEXT,
                aciklama TEXT,
                aktif INTEGER NOT NULL DEFAULT 1,
                olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                guncelleme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (kategori_id) REFERENCES kategoriler(id),
                FOREIGN KEY (tedarikci_id) REFERENCES tedarikciler(id)
            );

            CREATE TABLE IF NOT EXISTS stok_hareketleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_id INTEGER NOT NULL,
                hareket_tipi TEXT NOT NULL CHECK(hareket_tipi IN ('giris','cikis','iade','sayim','transfer')),
                miktar REAL NOT NULL,
                onceki_stok REAL NOT NULL,
                sonraki_stok REAL NOT NULL,
                birim_fiyat REAL,
                toplam_tutar REAL,
                belge_no TEXT,
                aciklama TEXT,
                yapan TEXT,
                tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (urun_id) REFERENCES urunler(id)
            );

            CREATE TABLE IF NOT EXISTS ayarlar (
                anahtar TEXT PRIMARY KEY,
                deger TEXT NOT NULL
            );

            INSERT OR IGNORE INTO ayarlar VALUES ('firma_adi', 'Benim Firmam');
            INSERT OR IGNORE INTO ayarlar VALUES ('para_birimi', 'TL');
            INSERT OR IGNORE INTO ayarlar VALUES ('dusuk_stok_uyari', '1');
            INSERT OR IGNORE INTO kategoriler (ad, aciklama) VALUES ('Genel', 'Genel kategori');
        """)
