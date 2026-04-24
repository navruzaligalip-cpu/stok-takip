#!/usr/bin/env python3
"""
Stok Takip Programı
Tam özellikli terminal tabanlı stok yönetim sistemi.
Çalıştırma: python3 main.py
"""
import sys
from veritabani import tablolari_olustur, veritabani
from utils import (
    baslik, alt_baslik, basari, hata, uyari, bilgi,
    giris_al, evet_hayir, devam_et, ekrani_temizle,
    Renk, renkli, tarih_formatla
)
from urunler import urun_menusu
from stok import stok_menusu
from tedarikci import tedarikci_menusu
from raporlar import rapor_menusu, ozet_panel, kritik_stok_raporu


SURUMU = "1.0.0"


def ayarlar_menusu():
    while True:
        print(baslik("AYARLAR"))
        with veritabani() as db:
            ayarlar = {r["anahtar"]: r["deger"]
                       for r in db.execute("SELECT * FROM ayarlar").fetchall()}

        print(f"  {renkli('Mevcut Ayarlar:', Renk.CYAN, Renk.KALIN)}")
        print(f"  Firma Adı      : {ayarlar.get('firma_adi', '-')}")
        print(f"  Para Birimi    : {ayarlar.get('para_birimi', 'TL')}")
        print(f"  Düşük Stok Uyarısı: {'Açık' if ayarlar.get('dusuk_stok_uyari') == '1' else 'Kapalı'}")
        print()
        print(f"  {renkli('1', Renk.SARI)}) Firma Adını Değiştir")
        print(f"  {renkli('2', Renk.SARI)}) Para Birimini Değiştir")
        print(f"  {renkli('3', Renk.SARI)}) Düşük Stok Uyarısını Aç/Kapat")
        print(f"  {renkli('0', Renk.KIRMIZI)}) Geri")
        secim = input(renkli("\n  Seçiminiz: ", Renk.BEYAZ)).strip()

        if secim == "1":
            yeni = giris_al("Yeni firma adı", varsayilan=ayarlar.get("firma_adi", ""))
            with veritabani() as db:
                db.execute("UPDATE ayarlar SET deger=? WHERE anahtar='firma_adi'", (yeni,))
            print(basari("Firma adı güncellendi."))
            devam_et()
        elif secim == "2":
            yeni = giris_al("Para birimi (TL, USD, EUR vb.)", varsayilan=ayarlar.get("para_birimi", "TL"))
            with veritabani() as db:
                db.execute("UPDATE ayarlar SET deger=? WHERE anahtar='para_birimi'", (yeni,))
            print(basari("Para birimi güncellendi."))
            devam_et()
        elif secim == "3":
            mevcut = ayarlar.get("dusuk_stok_uyari", "1")
            yeni = "0" if mevcut == "1" else "1"
            with veritabani() as db:
                db.execute("UPDATE ayarlar SET deger=? WHERE anahtar='dusuk_stok_uyari'", (yeni,))
            durum = "açıldı" if yeni == "1" else "kapatıldı"
            print(basari(f"Düşük stok uyarısı {durum}."))
            devam_et()
        elif secim == "0":
            break


def hakkinda():
    print(baslik("HAKKINDA"))
    print(f"""
  {renkli('Stok Takip Programı', Renk.CYAN, Renk.KALIN)}
  Sürüm  : {SURUMU}

  {renkli('Özellikler:', Renk.CYAN)}
  • Ürün ve Kategori Yönetimi
  • Tedarikçi Yönetimi
  • Stok Girişi / Çıkışı / İadesi
  • Toplu Stok İşlemleri
  • Stok Sayımı
  • Kritik Stok Uyarıları
  • Kâr / Zarar Analizi
  • Hareket Geçmişi
  • Çoklu Raporlar

  {renkli('Teknik Bilgi:', Renk.CYAN)}
  • Dil    : Python 3
  • Veritabanı : SQLite
  • Harici bağımlılık yok

  {renkli('Kullanım İpuçları:', Renk.CYAN)}
  • Ürün aramada kısmi ad, tam kod veya barkod girebilirsiniz.
  • Bir alan için varsayılan değeri korumak üzere Enter'a basın.
  • Kritik stok uyarısı için minimum stok değerini doğru girin.
    """)
    devam_et()


def giris_ekrani(firma_adi: str):
    ekrani_temizle()
    print(renkli("""
  ╔══════════════════════════════════════════════════════════╗
  ║         STOK TAKİP ve YÖNETİM SİSTEMİ                   ║
  ╚══════════════════════════════════════════════════════════╝""", Renk.MAVI, Renk.KALIN))
    print(renkli(f"  Firma: {firma_adi}", Renk.CYAN))
    print()


def kritik_stok_kontrol():
    with veritabani() as db:
        uyari_aktif = db.execute(
            "SELECT deger FROM ayarlar WHERE anahtar='dusuk_stok_uyari'"
        ).fetchone()
        if uyari_aktif and uyari_aktif["deger"] == "0":
            return
        sayim = db.execute(
            "SELECT COUNT(*) as c FROM urunler WHERE aktif=1 AND stok_miktari <= minimum_stok"
        ).fetchone()["c"]
        if sayim > 0:
            print(uyari(
                f"{sayim} ürün kritik stok seviyesinde veya tükendi! "
                f"(Raporlar → Kritik Stok Raporu)"
            ))


def ana_menu():
    tablolari_olustur()

    with veritabani() as db:
        row = db.execute("SELECT deger FROM ayarlar WHERE anahtar='firma_adi'").fetchone()
        firma_adi = row["deger"] if row else "Firma"

    while True:
        giris_ekrani(firma_adi)
        kritik_stok_kontrol()
        print(f"""
  {renkli('ANA MENÜ', Renk.MAVI, Renk.KALIN)}

  {renkli('1', Renk.SARI, Renk.KALIN)}) 📦  Ürün Yönetimi
  {renkli('2', Renk.SARI, Renk.KALIN)}) 🔄  Stok Hareketleri
  {renkli('3', Renk.SARI, Renk.KALIN)}) 🏭  Tedarikçi Yönetimi
  {renkli('4', Renk.SARI, Renk.KALIN)}) 📊  Raporlar ve Analiz
  {renkli('5', Renk.SARI, Renk.KALIN)}) ⚙   Ayarlar
  {renkli('6', Renk.SARI, Renk.KALIN)}) ℹ   Hakkında

  {renkli('0', Renk.KIRMIZI, Renk.KALIN)}) 🚪  Çıkış
""")
        secim = input(renkli("  Seçiminiz: ", Renk.BEYAZ)).strip()

        if secim == "1":
            urun_menusu()
        elif secim == "2":
            stok_menusu()
        elif secim == "3":
            tedarikci_menusu()
        elif secim == "4":
            rapor_menusu()
        elif secim == "5":
            ayarlar_menusu()
        elif secim == "6":
            hakkinda()
        elif secim == "0":
            if evet_hayir("Çıkmak istiyor musunuz?", varsayilan=True):
                print(renkli("\n  İyi çalışmalar! Görüşürüz.\n", Renk.CYAN, Renk.KALIN))
                sys.exit(0)
        else:
            print(hata("Geçersiz seçim! Lütfen listeden bir numara giriniz."))
            devam_et()


if __name__ == "__main__":
    try:
        ana_menu()
    except KeyboardInterrupt:
        print(renkli("\n\n  Program sonlandırıldı.\n", Renk.SARI))
        sys.exit(0)
