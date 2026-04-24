"""Tedarikçi yönetimi işlemleri."""
from veritabani import veritabani
from utils import (
    baslik, alt_baslik, basari, hata, uyari, bilgi,
    tablo_yazdir, giris_al, sayi_giris_al, evet_hayir,
    devam_et, para_formatla, tarih_formatla, Renk, renkli
)


def tedarikci_listele():
    print(baslik("TEDARİKÇİ LİSTESİ"))
    with veritabani() as db:
        rows = db.execute("""
            SELECT t.id, t.ad, t.telefon, t.eposta,
                   t.vergi_no, COUNT(u.id) as urun_sayisi,
                   t.olusturma_tarihi
            FROM tedarikciler t
            LEFT JOIN urunler u ON u.tedarikci_id=t.id
            GROUP BY t.id ORDER BY t.ad
        """).fetchall()

    if not rows:
        print(bilgi("Henüz tedarikçi eklenmemiş."))
        devam_et()
        return

    tablo_yazdir(
        ["ID", "Tedarikçi Adı", "Telefon", "E-posta", "Vergi No",
         "Ürün Sayısı", "Eklenme"],
        [[r["id"], r["ad"], r["telefon"] or "-", r["eposta"] or "-",
          r["vergi_no"] or "-", r["urun_sayisi"],
          tarih_formatla(r["olusturma_tarihi"])]
         for r in rows]
    )
    devam_et()


def tedarikci_ekle():
    print(baslik("YENİ TEDARİKÇİ EKLE"))
    ad = giris_al("Tedarikçi adı / Firma adı")
    telefon  = giris_al("Telefon", zorunlu=False)
    eposta   = giris_al("E-posta", zorunlu=False)
    adres    = giris_al("Adres", zorunlu=False)
    vergi_no = giris_al("Vergi numarası", zorunlu=False)

    with veritabani() as db:
        db.execute(
            "INSERT INTO tedarikciler (ad, telefon, eposta, adres, vergi_no) VALUES (?,?,?,?,?)",
            (ad, telefon or None, eposta or None, adres or None, vergi_no or None)
        )
        print(basari(f"'{ad}' tedarikçisi eklendi."))
    devam_et()


def tedarikci_detay():
    print(baslik("TEDARİKÇİ DETAYI"))
    tid = int(giris_al("Tedarikçi ID"))
    with veritabani() as db:
        t = db.execute("SELECT * FROM tedarikciler WHERE id=?", (tid,)).fetchone()
        if not t:
            print(hata("Tedarikçi bulunamadı!"))
            devam_et()
            return

        print(f"\n  {renkli('Ad:', Renk.CYAN)}          {t['ad']}")
        print(f"  {renkli('Telefon:', Renk.CYAN)}      {t['telefon'] or '-'}")
        print(f"  {renkli('E-posta:', Renk.CYAN)}      {t['eposta'] or '-'}")
        print(f"  {renkli('Adres:', Renk.CYAN)}        {t['adres'] or '-'}")
        print(f"  {renkli('Vergi No:', Renk.CYAN)}     {t['vergi_no'] or '-'}")
        print(f"  {renkli('Eklenme:', Renk.CYAN)}      {tarih_formatla(t['olusturma_tarihi'])}")

        urunler = db.execute(
            "SELECT id, kod, ad, stok_miktari, birim FROM urunler WHERE tedarikci_id=? AND aktif=1",
            (tid,)
        ).fetchall()
        if urunler:
            print(alt_baslik("Bu Tedarikçinin Ürünleri"))
            tablo_yazdir(
                ["ID", "Kod", "Ürün Adı", "Stok", "Birim"],
                [[u["id"], u["kod"], u["ad"],
                  u["stok_miktari"], u["birim"]] for u in urunler]
            )
    devam_et()


def tedarikci_guncelle():
    print(baslik("TEDARİKÇİ GÜNCELLE"))
    tid = int(giris_al("Güncellenecek tedarikçi ID"))
    with veritabani() as db:
        t = db.execute("SELECT * FROM tedarikciler WHERE id=?", (tid,)).fetchone()
        if not t:
            print(hata("Tedarikçi bulunamadı!"))
            devam_et()
            return

        print(bilgi("Değiştirmek istemediğiniz alanlar için Enter'a basın.\n"))
        ad = giris_al("Ad", varsayilan=t["ad"])
        telefon  = giris_al("Telefon", varsayilan=t["telefon"] or "", zorunlu=False)
        eposta   = giris_al("E-posta", varsayilan=t["eposta"] or "", zorunlu=False)
        adres    = giris_al("Adres", varsayilan=t["adres"] or "", zorunlu=False)
        vergi_no = giris_al("Vergi No", varsayilan=t["vergi_no"] or "", zorunlu=False)

        db.execute("""
            UPDATE tedarikciler SET ad=?, telefon=?, eposta=?, adres=?, vergi_no=?
            WHERE id=?
        """, (ad, telefon or None, eposta or None, adres or None,
              vergi_no or None, tid))
        print(basari(f"'{ad}' tedarikçisi güncellendi."))
    devam_et()


def tedarikci_sil():
    print(baslik("TEDARİKÇİ SİL"))
    tid = int(giris_al("Silinecek tedarikçi ID"))
    with veritabani() as db:
        t = db.execute("SELECT * FROM tedarikciler WHERE id=?", (tid,)).fetchone()
        if not t:
            print(hata("Tedarikçi bulunamadı!"))
            devam_et()
            return

        urun_sayisi = db.execute(
            "SELECT COUNT(*) as c FROM urunler WHERE tedarikci_id=?", (tid,)
        ).fetchone()["c"]

        if urun_sayisi > 0:
            print(uyari(f"Bu tedarikçiye bağlı {urun_sayisi} ürün var."))
            if not evet_hayir("Ürünlerin tedarikçi bilgisi kaldırılacak. Devam edilsin mi?", False):
                print(bilgi("İşlem iptal edildi."))
                devam_et()
                return
            db.execute("UPDATE urunler SET tedarikci_id=NULL WHERE tedarikci_id=?", (tid,))

        if evet_hayir(f"'{t['ad']}' tedarikçisini silmek istiyor musunuz?", False):
            db.execute("DELETE FROM tedarikciler WHERE id=?", (tid,))
            print(basari("Tedarikçi silindi."))
        else:
            print(bilgi("İşlem iptal edildi."))
    devam_et()


def tedarikci_menusu():
    while True:
        print(baslik("TEDARİKÇİ YÖNETİMİ"))
        print(f"  {renkli('1', Renk.SARI)}) Tedarikçileri Listele")
        print(f"  {renkli('2', Renk.SARI)}) Tedarikçi Detayı")
        print(f"  {renkli('3', Renk.SARI)}) Yeni Tedarikçi Ekle")
        print(f"  {renkli('4', Renk.SARI)}) Tedarikçi Güncelle")
        print(f"  {renkli('5', Renk.SARI)}) Tedarikçi Sil")
        print(f"  {renkli('0', Renk.KIRMIZI)}) Ana Menüye Dön")
        secim = input(renkli("\n  Seçiminiz: ", Renk.BEYAZ)).strip()

        if secim == "1":
            tedarikci_listele()
        elif secim == "2":
            tedarikci_detay()
        elif secim == "3":
            tedarikci_ekle()
        elif secim == "4":
            tedarikci_guncelle()
        elif secim == "5":
            tedarikci_sil()
        elif secim == "0":
            break
        else:
            print(hata("Geçersiz seçim!"))
