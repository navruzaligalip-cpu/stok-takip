"""Stok giriş, çıkış, iade, sayım ve transfer işlemleri."""
from veritabani import veritabani
from utils import (
    baslik, alt_baslik, basari, hata, uyari, bilgi,
    tablo_yazdir, giris_al, sayi_giris_al, evet_hayir,
    devam_et, para_formatla, tarih_formatla, Renk, renkli, simdi
)


def _urun_bul(db, arama: str):
    """Kod, barkod veya ad ile ürün arar."""
    return db.execute("""
        SELECT u.*, k.ad as kategori_adi
        FROM urunler u
        LEFT JOIN kategoriler k ON k.id=u.kategori_id
        WHERE (u.kod=? OR u.barkod=? OR u.ad LIKE ?) AND u.aktif=1
    """, (arama, arama, f"%{arama}%")).fetchall()


def _urun_sec(db) -> dict:
    """Kullanıcıdan ürün seçtirip döner."""
    while True:
        arama = giris_al("Ürün kodu, barkod veya ad ile ara")
        sonuclar = _urun_bul(db, arama)
        if not sonuclar:
            print(hata("Ürün bulunamadı!"))
            if not evet_hayir("Tekrar aramak ister misiniz?"):
                return None
            continue
        if len(sonuclar) == 1:
            return sonuclar[0]
        # Birden fazla sonuç
        tablo_yazdir(
            ["#", "ID", "Kod", "Ürün Adı", "Stok", "Birim"],
            [[i + 1, r["id"], r["kod"], r["ad"],
              r["stok_miktari"], r["birim"]]
             for i, r in enumerate(sonuclar)]
        )
        idx = int(sayi_giris_al("Sıra numarası seçin", minimum=1,
                                maksimum=len(sonuclar), tam_sayi=True)) - 1
        return sonuclar[idx]


def _hareket_kaydet(db, urun_id: int, tip: str, miktar: float,
                    birim_fiyat: float, aciklama: str, belge_no: str,
                    yapan: str) -> float:
    onceki = db.execute(
        "SELECT stok_miktari FROM urunler WHERE id=?", (urun_id,)
    ).fetchone()["stok_miktari"]

    if tip == "cikis" and miktar > onceki:
        raise ValueError(
            f"Yetersiz stok! Mevcut: {onceki:.2f}, İstenen: {miktar:.2f}"
        )

    sonraki = onceki + miktar if tip in ("giris", "iade") else onceki - miktar
    if tip == "sayim":
        sonraki = miktar

    db.execute(
        "UPDATE urunler SET stok_miktari=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
        (sonraki, urun_id)
    )
    db.execute("""
        INSERT INTO stok_hareketleri
          (urun_id, hareket_tipi, miktar, onceki_stok, sonraki_stok,
           birim_fiyat, toplam_tutar, belge_no, aciklama, yapan)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (urun_id, tip,
          abs(miktar if tip != "sayim" else sonraki - onceki),
          onceki, sonraki,
          birim_fiyat, abs(miktar) * birim_fiyat if birim_fiyat else None,
          belge_no or None, aciklama or None, yapan or "Kullanıcı"))
    return sonraki


# ─── STOK GİRİŞİ ─────────────────────────────────────────────────────────────
def stok_girisi():
    print(baslik("STOK GİRİŞİ (SATIN ALMA)"))
    with veritabani() as db:
        urun = _urun_sec(db)
        if not urun:
            return

        print(f"\n  {renkli('Ürün:', Renk.CYAN)} {urun['ad']}  |  "
              f"{renkli('Mevcut Stok:', Renk.CYAN)} "
              f"{renkli(str(urun['stok_miktari']), Renk.YESIL, Renk.KALIN)} {urun['birim']}\n")

        miktar = sayi_giris_al(f"Giriş miktarı ({urun['birim']})", minimum=0.001)
        birim_fiyat = sayi_giris_al("Birim alış fiyatı", varsayilan=urun["alis_fiyati"])
        belge_no = giris_al("İrsaliye/Fatura no", zorunlu=False)
        aciklama = giris_al("Açıklama", varsayilan="Stok girişi", zorunlu=False)
        yapan = giris_al("İşlemi yapan", varsayilan="Kullanıcı", zorunlu=False)

        toplam = miktar * birim_fiyat
        print(f"\n  {renkli('Toplam tutar:', Renk.CYAN)} {para_formatla(toplam)}")
        if not evet_hayir("İşlemi onaylıyor musunuz?"):
            print(bilgi("İşlem iptal edildi."))
            devam_et()
            return

        yeni_stok = _hareket_kaydet(db, urun["id"], "giris", miktar,
                                     birim_fiyat, aciklama, belge_no, yapan)
        print(basari(f"Stok girişi yapıldı. Yeni stok: {yeni_stok:.2f} {urun['birim']}"))

        # Fiyat güncelle?
        if birim_fiyat != urun["alis_fiyati"]:
            if evet_hayir("Alış fiyatını güncellemek ister misiniz?"):
                db.execute("UPDATE urunler SET alis_fiyati=? WHERE id=?",
                           (birim_fiyat, urun["id"]))
                print(basari("Alış fiyatı güncellendi."))
    devam_et()


# ─── STOK ÇIKIŞI ─────────────────────────────────────────────────────────────
def stok_cikisi():
    print(baslik("STOK ÇIKIŞI (SATIŞ)"))
    with veritabani() as db:
        urun = _urun_sec(db)
        if not urun:
            return

        if urun["stok_miktari"] <= 0:
            print(hata(f"Bu ürünün stoğu tükenmiş! Mevcut: {urun['stok_miktari']}"))
            devam_et()
            return

        print(f"\n  {renkli('Ürün:', Renk.CYAN)} {urun['ad']}  |  "
              f"{renkli('Mevcut Stok:', Renk.CYAN)} "
              f"{renkli(str(urun['stok_miktari']), Renk.YESIL, Renk.KALIN)} {urun['birim']}\n")

        miktar = sayi_giris_al(
            f"Çıkış miktarı ({urun['birim']})",
            minimum=0.001, maksimum=urun["stok_miktari"]
        )
        birim_fiyat = sayi_giris_al("Birim satış fiyatı", varsayilan=urun["satis_fiyati"])
        belge_no = giris_al("Sipariş/Fatura no", zorunlu=False)
        aciklama = giris_al("Açıklama", varsayilan="Stok çıkışı", zorunlu=False)
        yapan = giris_al("İşlemi yapan", varsayilan="Kullanıcı", zorunlu=False)

        toplam = miktar * birim_fiyat
        kar = (birim_fiyat - urun["alis_fiyati"]) * miktar
        print(f"\n  {renkli('Toplam tutar:', Renk.CYAN)} {para_formatla(toplam)}")
        print(f"  {renkli('Tahmini kâr:', Renk.CYAN)} "
              f"{renkli(para_formatla(kar), Renk.YESIL if kar >= 0 else Renk.KIRMIZI)}")

        if not evet_hayir("İşlemi onaylıyor musunuz?"):
            print(bilgi("İşlem iptal edildi."))
            devam_et()
            return

        try:
            yeni_stok = _hareket_kaydet(db, urun["id"], "cikis", miktar,
                                         birim_fiyat, aciklama, belge_no, yapan)
            print(basari(f"Stok çıkışı yapıldı. Yeni stok: {yeni_stok:.2f} {urun['birim']}"))
            if yeni_stok <= urun["minimum_stok"]:
                print(uyari(f"DİKKAT: Stok minimum seviyenin altına düştü! ({yeni_stok:.2f} / {urun['minimum_stok']:.2f})"))
        except ValueError as e:
            print(hata(str(e)))
    devam_et()


# ─── İADE ────────────────────────────────────────────────────────────────────
def stok_iade():
    print(baslik("İADE İŞLEMİ"))
    with veritabani() as db:
        urun = _urun_sec(db)
        if not urun:
            return

        print(f"\n  {renkli('Ürün:', Renk.CYAN)} {urun['ad']}  |  "
              f"{renkli('Mevcut Stok:', Renk.CYAN)} {urun['stok_miktari']} {urun['birim']}\n")

        miktar = sayi_giris_al(f"İade miktarı ({urun['birim']})", minimum=0.001)
        birim_fiyat = sayi_giris_al("Birim fiyat", varsayilan=urun["satis_fiyati"])
        belge_no = giris_al("İade no / Belge no", zorunlu=False)
        aciklama = giris_al("İade sebebi", varsayilan="Müşteri iadesi")
        yapan = giris_al("İşlemi yapan", varsayilan="Kullanıcı", zorunlu=False)

        if not evet_hayir("İşlemi onaylıyor musunuz?"):
            print(bilgi("İşlem iptal edildi."))
            devam_et()
            return

        yeni_stok = _hareket_kaydet(db, urun["id"], "iade", miktar,
                                     birim_fiyat, aciklama, belge_no, yapan)
        print(basari(f"İade işlendi. Yeni stok: {yeni_stok:.2f} {urun['birim']}"))
    devam_et()


# ─── STOK SAYIMI ──────────────────────────────────────────────────────────────
def stok_sayimi():
    print(baslik("STOK SAYIMI"))
    print(uyari("Sayım sonucu gerçek stok miktarını doğrudan günceller."))
    with veritabani() as db:
        urun = _urun_sec(db)
        if not urun:
            return

        print(f"\n  {renkli('Ürün:', Renk.CYAN)} {urun['ad']}")
        print(f"  {renkli('Sistemdeki Stok:', Renk.CYAN)} "
              f"{renkli(str(urun['stok_miktari']), Renk.SARI, Renk.KALIN)} {urun['birim']}\n")

        gercek = sayi_giris_al(f"Sayılan gerçek miktar ({urun['birim']})", minimum=0)
        fark = gercek - urun["stok_miktari"]
        fark_str = renkli(
            f"{fark:+.2f}",
            Renk.YESIL if fark >= 0 else Renk.KIRMIZI
        )
        print(f"  Fark: {fark_str} {urun['birim']}")
        aciklama = giris_al("Açıklama", varsayilan="Stok sayımı")
        yapan = giris_al("Sayımı yapan", varsayilan="Kullanıcı", zorunlu=False)

        if not evet_hayir("Stoku güncellemek istiyor musunuz?"):
            print(bilgi("İşlem iptal edildi."))
            devam_et()
            return

        db.execute(
            "UPDATE urunler SET stok_miktari=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
            (gercek, urun["id"])
        )
        db.execute("""
            INSERT INTO stok_hareketleri
              (urun_id, hareket_tipi, miktar, onceki_stok, sonraki_stok,
               aciklama, yapan)
            VALUES (?,?,?,?,?,?,?)
        """, (urun["id"], "sayim", abs(fark),
              urun["stok_miktari"], gercek, aciklama, yapan))
        print(basari(f"Stok güncellendi. Yeni miktar: {gercek:.2f} {urun['birim']}"))
    devam_et()


# ─── HAREKET GEÇMİŞİ ─────────────────────────────────────────────────────────
def hareket_gecmisi():
    print(baslik("STOK HAREKET GEÇMİŞİ"))
    with veritabani() as db:
        urun = _urun_sec(db)
        if not urun:
            return

        print(alt_baslik(f"{urun['ad']} - Hareket Geçmişi"))
        hareketler = db.execute("""
            SELECT h.id, h.hareket_tipi, h.miktar, h.onceki_stok,
                   h.sonraki_stok, h.birim_fiyat, h.toplam_tutar,
                   h.belge_no, h.aciklama, h.yapan, h.tarih
            FROM stok_hareketleri h
            WHERE h.urun_id=?
            ORDER BY h.tarih DESC
            LIMIT 50
        """, (urun["id"],)).fetchall()

        if not hareketler:
            print(bilgi("Hareket kaydı bulunamadı."))
            devam_et()
            return

        tip_renk = {
            "giris": Renk.YESIL,
            "cikis": Renk.KIRMIZI,
            "iade": Renk.SARI,
            "sayim": Renk.CYAN,
            "transfer": Renk.MAGENTA,
        }
        satirlar = []
        renkler = []
        for h in hareketler:
            renk = tip_renk.get(h["hareket_tipi"], "")
            satirlar.append([
                h["id"],
                renkli(h["hareket_tipi"].upper(), renk),
                f"{h['miktar']:.2f}",
                f"{h['onceki_stok']:.2f}",
                f"{h['sonraki_stok']:.2f}",
                para_formatla(h["toplam_tutar"]) if h["toplam_tutar"] else "-",
                h["belge_no"] or "-",
                h["aciklama"] or "-",
                h["yapan"] or "-",
                tarih_formatla(h["tarih"]),
            ])
            renkler.append("")

        tablo_yazdir(
            ["ID", "Tip", "Miktar", "Önceki", "Sonraki",
             "Tutar", "Belge No", "Açıklama", "Yapan", "Tarih"],
            satirlar, renkler
        )
    devam_et()


# ─── TOPLU GİRİŞ ─────────────────────────────────────────────────────────────
def toplu_stok_girisi():
    print(baslik("TOPLU STOK GİRİŞİ"))
    print(bilgi("Birden fazla ürün için aynı irsaliye üzerinden giriş yapın."))
    belge_no = giris_al("İrsaliye/Fatura no", zorunlu=False)
    yapan = giris_al("İşlemi yapan", varsayilan="Kullanıcı", zorunlu=False)
    kalemler = []

    with veritabani() as db:
        while True:
            print(alt_baslik(f"Kalem {len(kalemler) + 1}"))
            urun = _urun_sec(db)
            if not urun:
                break
            miktar = sayi_giris_al(f"Miktar ({urun['birim']})", minimum=0.001)
            birim_fiyat = sayi_giris_al("Birim fiyat", varsayilan=urun["alis_fiyati"])
            kalemler.append((urun, miktar, birim_fiyat))
            if not evet_hayir("Başka ürün eklemek istiyor musunuz?", varsayilan=True):
                break

        if not kalemler:
            print(bilgi("İşlem iptal edildi."))
            devam_et()
            return

        print(alt_baslik("Özet"))
        toplam_tutar = 0
        for urun, miktar, birim_fiyat in kalemler:
            tutar = miktar * birim_fiyat
            toplam_tutar += tutar
            print(f"  {urun['ad']}: {miktar:.2f} {urun['birim']} x {para_formatla(birim_fiyat)} = {para_formatla(tutar)}")
        print(f"\n  {renkli('TOPLAM:', Renk.KALIN, Renk.CYAN)} {para_formatla(toplam_tutar)}")

        if not evet_hayir("Tüm işlemleri onaylıyor musunuz?"):
            print(bilgi("İşlem iptal edildi."))
            devam_et()
            return

        for urun, miktar, birim_fiyat in kalemler:
            _hareket_kaydet(db, urun["id"], "giris", miktar,
                            birim_fiyat, "Toplu stok girişi", belge_no, yapan)

        print(basari(f"{len(kalemler)} ürün için stok girişi tamamlandı."))
    devam_et()


# ─── MENÜ ─────────────────────────────────────────────────────────────────────
def stok_menusu():
    while True:
        print(baslik("STOK HAREKETLERİ"))
        print(f"  {renkli('1', Renk.SARI)}) Stok Girişi (Satın Alma)")
        print(f"  {renkli('2', Renk.SARI)}) Stok Çıkışı (Satış)")
        print(f"  {renkli('3', Renk.SARI)}) İade İşlemi")
        print(f"  {renkli('4', Renk.SARI)}) Stok Sayımı")
        print(f"  {renkli('5', Renk.SARI)}) Toplu Stok Girişi")
        print(f"  {renkli('6', Renk.SARI)}) Hareket Geçmişi (Ürün Bazlı)")
        print(f"  {renkli('0', Renk.KIRMIZI)}) Ana Menüye Dön")
        secim = input(renkli("\n  Seçiminiz: ", Renk.BEYAZ)).strip()

        if secim == "1":
            stok_girisi()
        elif secim == "2":
            stok_cikisi()
        elif secim == "3":
            stok_iade()
        elif secim == "4":
            stok_sayimi()
        elif secim == "5":
            toplu_stok_girisi()
        elif secim == "6":
            hareket_gecmisi()
        elif secim == "0":
            break
        else:
            print(hata("Geçersiz seçim!"))
