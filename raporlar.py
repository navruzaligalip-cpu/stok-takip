"""Stok raporları ve analizleri."""
from veritabani import veritabani
from utils import (
    baslik, alt_baslik, basari, hata, uyari, bilgi,
    tablo_yazdir, giris_al, sayi_giris_al, evet_hayir,
    devam_et, para_formatla, tarih_formatla, Renk, renkli
)


# ─── ÖZET GÖSTERGE PANELİ ────────────────────────────────────────────────────
def ozet_panel():
    print(baslik("ÖZET GÖSTERGE PANELİ", 70))
    with veritabani() as db:
        toplam_urun = db.execute(
            "SELECT COUNT(*) as c FROM urunler WHERE aktif=1"
        ).fetchone()["c"]

        kritik_stok = db.execute(
            "SELECT COUNT(*) as c FROM urunler WHERE aktif=1 AND stok_miktari <= minimum_stok"
        ).fetchone()["c"]

        sifir_stok = db.execute(
            "SELECT COUNT(*) as c FROM urunler WHERE aktif=1 AND stok_miktari <= 0"
        ).fetchone()["c"]

        toplam_stok_degeri = db.execute(
            "SELECT SUM(stok_miktari * alis_fiyati) as toplam FROM urunler WHERE aktif=1"
        ).fetchone()["toplam"] or 0

        toplam_satis_degeri = db.execute(
            "SELECT SUM(stok_miktari * satis_fiyati) as toplam FROM urunler WHERE aktif=1"
        ).fetchone()["toplam"] or 0

        bugun_giris = db.execute("""
            SELECT COALESCE(SUM(toplam_tutar), 0) as t
            FROM stok_hareketleri
            WHERE hareket_tipi='giris' AND DATE(tarih)=DATE('now')
        """).fetchone()["t"]

        bugun_cikis = db.execute("""
            SELECT COALESCE(SUM(toplam_tutar), 0) as t
            FROM stok_hareketleri
            WHERE hareket_tipi='cikis' AND DATE(tarih)=DATE('now')
        """).fetchone()["t"]

        bu_ay_giris = db.execute("""
            SELECT COALESCE(SUM(toplam_tutar), 0) as t
            FROM stok_hareketleri
            WHERE hareket_tipi='giris' AND strftime('%Y-%m', tarih)=strftime('%Y-%m','now')
        """).fetchone()["t"]

        bu_ay_cikis = db.execute("""
            SELECT COALESCE(SUM(toplam_tutar), 0) as t
            FROM stok_hareketleri
            WHERE hareket_tipi='cikis' AND strftime('%Y-%m', tarih)=strftime('%Y-%m','now')
        """).fetchone()["t"]

        kategori_sayisi = db.execute(
            "SELECT COUNT(*) as c FROM kategoriler"
        ).fetchone()["c"]

        tedarikci_sayisi = db.execute(
            "SELECT COUNT(*) as c FROM tedarikciler"
        ).fetchone()["c"]

    cizgi = "─" * 70
    print(renkli(f"\n  {'GENEL BİLGİLER':^66}", Renk.MAVI, Renk.KALIN))
    print(renkli(f"  {cizgi}", Renk.GRI))
    print(f"  {renkli('Toplam Ürün (Aktif):', Renk.CYAN):<35} {toplam_urun}")
    print(f"  {renkli('Kategori Sayısı:', Renk.CYAN):<35} {kategori_sayisi}")
    print(f"  {renkli('Tedarikçi Sayısı:', Renk.CYAN):<35} {tedarikci_sayisi}")

    print(renkli(f"\n  {'STOK DURUMU':^66}", Renk.MAVI, Renk.KALIN))
    print(renkli(f"  {cizgi}", Renk.GRI))
    stok_degeri_str = para_formatla(toplam_stok_degeri)
    satis_degeri_str = para_formatla(toplam_satis_degeri)
    kar_potansiyeli = toplam_satis_degeri - toplam_stok_degeri
    print(f"  {renkli('Toplam Stok Değeri (Alış):', Renk.CYAN):<35} {renkli(stok_degeri_str, Renk.YESIL)}")
    print(f"  {renkli('Toplam Stok Değeri (Satış):', Renk.CYAN):<35} {renkli(satis_degeri_str, Renk.YESIL)}")
    kar_renk = Renk.YESIL if kar_potansiyeli >= 0 else Renk.KIRMIZI
    print(f"  {renkli('Potansiyel Kâr:', Renk.CYAN):<35} {renkli(para_formatla(kar_potansiyeli), kar_renk)}")
    kritik_renk = Renk.KIRMIZI if kritik_stok > 0 else Renk.YESIL
    print(f"  {renkli('Kritik Stok Ürün Sayısı:', Renk.CYAN):<35} {renkli(str(kritik_stok), kritik_renk, Renk.KALIN)}")
    sifir_renk = Renk.KIRMIZI if sifir_stok > 0 else Renk.YESIL
    print(f"  {renkli('Stoku Tükenen Ürün Sayısı:', Renk.CYAN):<35} {renkli(str(sifir_stok), sifir_renk, Renk.KALIN)}")

    print(renkli(f"\n  {'HAREKETLİLİK':^66}", Renk.MAVI, Renk.KALIN))
    print(renkli(f"  {cizgi}", Renk.GRI))
    print(f"  {renkli('Bugün Giriş Tutarı:', Renk.CYAN):<35} {para_formatla(bugun_giris)}")
    print(f"  {renkli('Bugün Çıkış Tutarı:', Renk.CYAN):<35} {para_formatla(bugun_cikis)}")
    print(f"  {renkli('Bu Ay Giriş Tutarı:', Renk.CYAN):<35} {para_formatla(bu_ay_giris)}")
    print(f"  {renkli('Bu Ay Çıkış Tutarı:', Renk.CYAN):<35} {para_formatla(bu_ay_cikis)}")
    print()
    devam_et()


# ─── KRİTİK STOK RAPORU ───────────────────────────────────────────────────────
def kritik_stok_raporu():
    print(baslik("KRİTİK STOK RAPORU"))
    with veritabani() as db:
        rows = db.execute("""
            SELECT u.id, u.kod, u.ad, k.ad as kategori,
                   u.stok_miktari, u.minimum_stok, u.birim,
                   t.ad as tedarikci
            FROM urunler u
            LEFT JOIN kategoriler k ON k.id=u.kategori_id
            LEFT JOIN tedarikciler t ON t.id=u.tedarikci_id
            WHERE u.aktif=1 AND u.stok_miktari <= u.minimum_stok
            ORDER BY u.stok_miktari ASC
        """).fetchall()

    if not rows:
        print(basari("Tüm ürünler yeterli stok seviyesinde!"))
        devam_et()
        return

    satirlar = []
    renkler = []
    for r in rows:
        stok = r["stok_miktari"]
        durum = renkli("TÜKENDI", Renk.KIRMIZI, Renk.KALIN) if stok <= 0 else \
                renkli("KRİTİK", Renk.SARI, Renk.KALIN)
        stok_renk = Renk.KIRMIZI if stok <= 0 else Renk.SARI
        satirlar.append([
            r["id"], r["kod"], r["ad"], r["kategori"] or "-",
            renkli(f"{stok:.2f}", stok_renk),
            f"{r['minimum_stok']:.2f}", r["birim"],
            r["tedarikci"] or "-", durum
        ])
        renkler.append("")

    tablo_yazdir(
        ["ID", "Kod", "Ürün Adı", "Kategori", "Stok", "Min.Stok",
         "Birim", "Tedarikçi", "Durum"],
        satirlar, renkler
    )
    print(uyari(f"{len(rows)} ürün kritik stok seviyesinde veya tükendi!"))
    devam_et()


# ─── STOK DEĞER RAPORU ───────────────────────────────────────────────────────
def stok_deger_raporu():
    print(baslik("STOK DEĞER RAPORU"))
    with veritabani() as db:
        rows = db.execute("""
            SELECT u.kod, u.ad, k.ad as kategori,
                   u.stok_miktari, u.birim,
                   u.alis_fiyati, u.satis_fiyati,
                   (u.stok_miktari * u.alis_fiyati) as alis_toplam,
                   (u.stok_miktari * u.satis_fiyati) as satis_toplam,
                   ((u.satis_fiyati - u.alis_fiyati) * u.stok_miktari) as kar_potansiyeli
            FROM urunler u
            LEFT JOIN kategoriler k ON k.id=u.kategori_id
            WHERE u.aktif=1 AND u.stok_miktari > 0
            ORDER BY alis_toplam DESC
        """).fetchall()

    if not rows:
        print(bilgi("Stokta ürün bulunamadı."))
        devam_et()
        return

    toplam_alis = sum(r["alis_toplam"] for r in rows)
    toplam_satis = sum(r["satis_toplam"] for r in rows)
    toplam_kar = toplam_satis - toplam_alis

    tablo_yazdir(
        ["Kod", "Ürün Adı", "Kategori", "Stok", "Birim",
         "Alış Değeri", "Satış Değeri", "Kâr Pot."],
        [[r["kod"], r["ad"], r["kategori"] or "-",
          f"{r['stok_miktari']:.2f}", r["birim"],
          para_formatla(r["alis_toplam"]),
          para_formatla(r["satis_toplam"]),
          para_formatla(r["kar_potansiyeli"])]
         for r in rows]
    )

    print(f"\n  {renkli('GENEL TOPLAM', Renk.KALIN, Renk.CYAN)}")
    print(f"  {renkli('Alış Değeri:', Renk.CYAN):<30} {renkli(para_formatla(toplam_alis), Renk.YESIL)}")
    print(f"  {renkli('Satış Değeri:', Renk.CYAN):<30} {renkli(para_formatla(toplam_satis), Renk.YESIL)}")
    renk = Renk.YESIL if toplam_kar >= 0 else Renk.KIRMIZI
    print(f"  {renkli('Potansiyel Kâr:', Renk.CYAN):<30} {renkli(para_formatla(toplam_kar), renk, Renk.KALIN)}")
    devam_et()


# ─── HAREKET RAPORU ──────────────────────────────────────────────────────────
def hareket_raporu():
    print(baslik("GENEL HAREKET RAPORU"))
    print(bilgi("Tarih aralığı giriniz (boş bırakırsanız tüm kayıtlar gelir)"))
    baslangic = giris_al("Başlangıç tarihi (YYYY-MM-DD)", zorunlu=False)
    bitis     = giris_al("Bitiş tarihi (YYYY-MM-DD)", zorunlu=False)

    kosullar = ["1=1"]
    params = []
    if baslangic:
        kosullar.append("DATE(h.tarih) >= DATE(?)")
        params.append(baslangic)
    if bitis:
        kosullar.append("DATE(h.tarih) <= DATE(?)")
        params.append(bitis)

    with veritabani() as db:
        rows = db.execute(f"""
            SELECT h.id, u.kod, u.ad, h.hareket_tipi, h.miktar,
                   h.onceki_stok, h.sonraki_stok, h.birim_fiyat,
                   h.toplam_tutar, h.belge_no, h.aciklama,
                   h.yapan, h.tarih
            FROM stok_hareketleri h
            JOIN urunler u ON u.id=h.urun_id
            WHERE {' AND '.join(kosullar)}
            ORDER BY h.tarih DESC
            LIMIT 200
        """, params).fetchall()

    if not rows:
        print(bilgi("Kayıt bulunamadı."))
        devam_et()
        return

    tip_renk = {
        "giris": Renk.YESIL, "cikis": Renk.KIRMIZI,
        "iade": Renk.SARI, "sayim": Renk.CYAN, "transfer": Renk.MAGENTA
    }
    satirlar = []
    for h in rows:
        renk = tip_renk.get(h["hareket_tipi"], "")
        satirlar.append([
            h["id"], h["kod"], h["ad"],
            renkli(h["hareket_tipi"].upper(), renk),
            f"{h['miktar']:.2f}",
            para_formatla(h["toplam_tutar"]) if h["toplam_tutar"] else "-",
            h["belge_no"] or "-",
            h["yapan"] or "-",
            tarih_formatla(h["tarih"]),
        ])

    tablo_yazdir(
        ["ID", "Kod", "Ürün", "Tip", "Miktar", "Tutar",
         "Belge No", "Yapan", "Tarih"],
        satirlar
    )
    devam_et()


# ─── KATEGORİ BAZLI RAPOR ────────────────────────────────────────────────────
def kategori_raporu():
    print(baslik("KATEGORİ BAZLI STOK RAPORU"))
    with veritabani() as db:
        rows = db.execute("""
            SELECT k.ad as kategori,
                   COUNT(u.id) as urun_sayisi,
                   SUM(u.stok_miktari) as toplam_stok,
                   SUM(u.stok_miktari * u.alis_fiyati) as alis_degeri,
                   SUM(u.stok_miktari * u.satis_fiyati) as satis_degeri,
                   SUM(CASE WHEN u.stok_miktari <= u.minimum_stok THEN 1 ELSE 0 END) as kritik_sayisi
            FROM kategoriler k
            LEFT JOIN urunler u ON u.kategori_id=k.id AND u.aktif=1
            GROUP BY k.id ORDER BY alis_degeri DESC
        """).fetchall()

    tablo_yazdir(
        ["Kategori", "Ürün", "Toplam Stok", "Alış Değeri",
         "Satış Değeri", "Kritik"],
        [[r["kategori"], r["urun_sayisi"] or 0,
          f"{(r['toplam_stok'] or 0):.2f}",
          para_formatla(r["alis_degeri"] or 0),
          para_formatla(r["satis_degeri"] or 0),
          renkli(str(r["kritik_sayisi"] or 0),
                 Renk.KIRMIZI if (r["kritik_sayisi"] or 0) > 0 else Renk.YESIL)]
         for r in rows]
    )
    devam_et()


# ─── EN ÇOK HAREKET EDEN ÜRÜNLER ─────────────────────────────────────────────
def en_cok_hareket():
    print(baslik("EN ÇOK HAREKET EDEN ÜRÜNLER"))
    with veritabani() as db:
        rows = db.execute("""
            SELECT u.kod, u.ad,
                   COUNT(h.id) as islem_sayisi,
                   SUM(CASE WHEN h.hareket_tipi='giris' THEN h.miktar ELSE 0 END) as toplam_giris,
                   SUM(CASE WHEN h.hareket_tipi='cikis' THEN h.miktar ELSE 0 END) as toplam_cikis,
                   SUM(CASE WHEN h.hareket_tipi='cikis' THEN h.toplam_tutar ELSE 0 END) as toplam_satis,
                   u.stok_miktari, u.birim
            FROM urunler u
            JOIN stok_hareketleri h ON h.urun_id=u.id
            GROUP BY u.id
            ORDER BY islem_sayisi DESC
            LIMIT 20
        """).fetchall()

    if not rows:
        print(bilgi("Hareket kaydı bulunamadı."))
        devam_et()
        return

    tablo_yazdir(
        ["Kod", "Ürün Adı", "İşlem", "Top.Giriş", "Top.Çıkış",
         "Satış Tutarı", "Mevcut Stok", "Birim"],
        [[r["kod"], r["ad"], r["islem_sayisi"],
          f"{r['toplam_giris']:.2f}", f"{r['toplam_cikis']:.2f}",
          para_formatla(r["toplam_satis"] or 0),
          f"{r['stok_miktari']:.2f}", r["birim"]]
         for r in rows]
    )
    devam_et()


# ─── SATIŞ KÂR ANALİZİ ───────────────────────────────────────────────────────
def kar_analizi():
    print(baslik("SATIŞ KÂR ANALİZİ"))
    print(bilgi("Tarih aralığı giriniz (boş = tüm kayıtlar)"))
    baslangic = giris_al("Başlangıç tarihi (YYYY-MM-DD)", zorunlu=False)
    bitis     = giris_al("Bitiş tarihi (YYYY-MM-DD)", zorunlu=False)

    kosullar = ["h.hareket_tipi='cikis'"]
    params = []
    if baslangic:
        kosullar.append("DATE(h.tarih) >= DATE(?)")
        params.append(baslangic)
    if bitis:
        kosullar.append("DATE(h.tarih) <= DATE(?)")
        params.append(bitis)

    with veritabani() as db:
        rows = db.execute(f"""
            SELECT u.kod, u.ad,
                   SUM(h.miktar) as toplam_miktar,
                   SUM(h.toplam_tutar) as toplam_gelir,
                   SUM(h.miktar * u.alis_fiyati) as toplam_maliyet,
                   SUM(h.toplam_tutar - h.miktar * u.alis_fiyati) as toplam_kar,
                   u.birim
            FROM stok_hareketleri h
            JOIN urunler u ON u.id=h.urun_id
            WHERE {' AND '.join(kosullar)}
            GROUP BY u.id
            ORDER BY toplam_kar DESC
        """, params).fetchall()

    if not rows:
        print(bilgi("Satış kaydı bulunamadı."))
        devam_et()
        return

    toplam_gelir = sum(r["toplam_gelir"] or 0 for r in rows)
    toplam_maliyet = sum(r["toplam_maliyet"] or 0 for r in rows)
    toplam_kar = toplam_gelir - toplam_maliyet

    tablo_yazdir(
        ["Kod", "Ürün Adı", "Miktar", "Birim", "Gelir",
         "Maliyet", "Kâr", "Kâr %"],
        [[r["kod"], r["ad"], f"{r['toplam_miktar']:.2f}", r["birim"],
          para_formatla(r["toplam_gelir"] or 0),
          para_formatla(r["toplam_maliyet"] or 0),
          para_formatla(r["toplam_kar"] or 0),
          f"{((r['toplam_kar'] or 0) / (r['toplam_maliyet'] or 1) * 100):.1f}%"]
         for r in rows]
    )

    kar_renk = Renk.YESIL if toplam_kar >= 0 else Renk.KIRMIZI
    print(f"\n  {renkli('TOPLAM', Renk.KALIN, Renk.CYAN)}")
    print(f"  {renkli('Toplam Gelir:', Renk.CYAN):<30} {renkli(para_formatla(toplam_gelir), Renk.YESIL)}")
    print(f"  {renkli('Toplam Maliyet:', Renk.CYAN):<30} {para_formatla(toplam_maliyet)}")
    print(f"  {renkli('Net Kâr:', Renk.CYAN):<30} {renkli(para_formatla(toplam_kar), kar_renk, Renk.KALIN)}")
    if toplam_maliyet > 0:
        oran = toplam_kar / toplam_maliyet * 100
        print(f"  {renkli('Kâr Marjı:', Renk.CYAN):<30} {renkli(f'%{oran:.1f}', kar_renk)}")
    devam_et()


# ─── RAPOR MENÜSÜ ────────────────────────────────────────────────────────────
def rapor_menusu():
    while True:
        print(baslik("RAPORLAR VE ANALİZ"))
        print(f"  {renkli('1', Renk.SARI)}) Özet Gösterge Paneli")
        print(f"  {renkli('2', Renk.SARI)}) Kritik Stok Raporu")
        print(f"  {renkli('3', Renk.SARI)}) Stok Değer Raporu")
        print(f"  {renkli('4', Renk.SARI)}) Genel Hareket Raporu")
        print(f"  {renkli('5', Renk.SARI)}) Kategori Bazlı Rapor")
        print(f"  {renkli('6', Renk.SARI)}) En Çok Hareket Eden Ürünler")
        print(f"  {renkli('7', Renk.SARI)}) Satış Kâr Analizi")
        print(f"  {renkli('0', Renk.KIRMIZI)}) Ana Menüye Dön")
        secim = input(renkli("\n  Seçiminiz: ", Renk.BEYAZ)).strip()

        if secim == "1":
            ozet_panel()
        elif secim == "2":
            kritik_stok_raporu()
        elif secim == "3":
            stok_deger_raporu()
        elif secim == "4":
            hareket_raporu()
        elif secim == "5":
            kategori_raporu()
        elif secim == "6":
            en_cok_hareket()
        elif secim == "7":
            kar_analizi()
        elif secim == "0":
            break
        else:
            print(hata("Geçersiz seçim!"))
