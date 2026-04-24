"""Ürün ve kategori yönetimi işlemleri."""
from veritabani import veritabani
from utils import (
    baslik, alt_baslik, basari, hata, uyari, bilgi,
    tablo_yazdir, giris_al, sayi_giris_al, evet_hayir,
    secim_al, devam_et, para_formatla, tarih_formatla,
    kod_uret, Renk, renkli
)


# ═══════════════════════════════════════════════════════
#  KATEGORİ İŞLEMLERİ
# ═══════════════════════════════════════════════════════

def kategori_listele():
    print(baslik("KATEGORİ LİSTESİ"))
    with veritabani() as db:
        rows = db.execute("""
            SELECT k.id, k.ad, k.aciklama,
                   COUNT(u.id) as urun_sayisi,
                   k.olusturma_tarihi
            FROM kategoriler k
            LEFT JOIN urunler u ON u.kategori_id = k.id
            GROUP BY k.id ORDER BY k.ad
        """).fetchall()

    tablo_yazdir(
        ["ID", "Kategori Adı", "Açıklama", "Ürün Sayısı", "Oluşturma"],
        [[r["id"], r["ad"], r["aciklama"] or "-",
          r["urun_sayisi"], tarih_formatla(r["olusturma_tarihi"])]
         for r in rows]
    )
    devam_et()


def kategori_ekle():
    print(baslik("YENİ KATEGORİ EKLE"))
    ad = giris_al("Kategori adı")
    aciklama = giris_al("Açıklama", zorunlu=False)

    with veritabani() as db:
        try:
            db.execute("INSERT INTO kategoriler (ad, aciklama) VALUES (?, ?)",
                       (ad, aciklama or None))
            print(basari(f"'{ad}' kategorisi eklendi."))
        except Exception as e:
            print(hata(f"Kategori eklenemedi: {e}"))
    devam_et()


def kategori_sil():
    print(baslik("KATEGORİ SİL"))
    with veritabani() as db:
        rows = db.execute("SELECT id, ad FROM kategoriler ORDER BY ad").fetchall()
        if not rows:
            print(bilgi("Kategori bulunamadı."))
            devam_et()
            return

        for r in rows:
            print(f"  {r['id']:3d}) {r['ad']}")
        kid = int(giris_al("Silinecek kategori ID"))

        kullanilan = db.execute(
            "SELECT COUNT(*) as c FROM urunler WHERE kategori_id=?", (kid,)
        ).fetchone()["c"]
        if kullanilan > 0:
            print(hata(f"Bu kategoride {kullanilan} ürün var, silinemez!"))
        else:
            kategori = db.execute("SELECT ad FROM kategoriler WHERE id=?", (kid,)).fetchone()
            if not kategori:
                print(hata("Kategori bulunamadı."))
            elif evet_hayir(f"'{kategori['ad']}' kategorisini silmek istiyor musunuz?", False):
                db.execute("DELETE FROM kategoriler WHERE id=?", (kid,))
                print(basari("Kategori silindi."))
            else:
                print(bilgi("İşlem iptal edildi."))
    devam_et()


def kategori_menusu():
    while True:
        print(baslik("KATEGORİ YÖNETİMİ"))
        print(f"  {renkli('1', Renk.SARI)}) Kategorileri Listele")
        print(f"  {renkli('2', Renk.SARI)}) Yeni Kategori Ekle")
        print(f"  {renkli('3', Renk.SARI)}) Kategori Sil")
        print(f"  {renkli('0', Renk.KIRMIZI)}) Geri")
        secim = input(renkli("\n  Seçiminiz: ", Renk.BEYAZ)).strip()
        if secim == "1":
            kategori_listele()
        elif secim == "2":
            kategori_ekle()
        elif secim == "3":
            kategori_sil()
        elif secim == "0":
            break
        else:
            print(hata("Geçersiz seçim!"))


# ═══════════════════════════════════════════════════════
#  ÜRÜN İŞLEMLERİ
# ═══════════════════════════════════════════════════════

def _kategori_sec(db) -> int:
    rows = db.execute("SELECT id, ad FROM kategoriler ORDER BY ad").fetchall()
    if not rows:
        db.execute("INSERT INTO kategoriler (ad) VALUES ('Genel')")
        rows = db.execute("SELECT id, ad FROM kategoriler ORDER BY ad").fetchall()
    secenekler = [r["ad"] for r in rows]
    idx = secim_al("Kategori seçin", secenekler, varsayilan=1)
    return rows[idx]["id"]


def urun_ekle():
    print(baslik("YENİ ÜRÜN EKLE"))
    with veritabani() as db:
        mevcut_kodlar = [r["kod"] for r in db.execute("SELECT kod FROM urunler").fetchall()]
        otomatik_kod = kod_uret("URN", mevcut_kodlar)

        kod = giris_al("Ürün kodu", varsayilan=otomatik_kod)
        if db.execute("SELECT id FROM urunler WHERE kod=?", (kod,)).fetchone():
            print(hata(f"'{kod}' kodu zaten kullanımda!"))
            devam_et()
            return

        ad = giris_al("Ürün adı")
        barkod = giris_al("Barkod", zorunlu=False)
        if barkod and db.execute("SELECT id FROM urunler WHERE barkod=?", (barkod,)).fetchone():
            print(hata("Bu barkod başka bir ürüne ait!"))
            devam_et()
            return

        print(alt_baslik("Kategori"))
        kategori_id = _kategori_sec(db)

        birimler = ["adet", "kg", "litre", "metre", "paket", "kutu", "ton", "gram"]
        print(alt_baslik("Birim"))
        birim_idx = secim_al("Birim seçin", birimler, varsayilan=1)
        birim = birimler[birim_idx]

        print(alt_baslik("Fiyat Bilgileri"))
        alis_fiyati  = sayi_giris_al("Alış fiyatı", varsayilan=0.0)
        satis_fiyati = sayi_giris_al("Satış fiyatı", varsayilan=0.0)
        kdv_orani    = sayi_giris_al("KDV oranı (%)", varsayilan=18.0, minimum=0, maksimum=100)

        print(alt_baslik("Stok Bilgileri"))
        ilk_stok     = sayi_giris_al("Başlangıç stok miktarı", varsayilan=0.0)
        minimum_stok = sayi_giris_al("Minimum stok uyarı seviyesi", varsayilan=5.0)
        maksimum_stok = sayi_giris_al("Maksimum stok seviyesi (0=sınırsız)", varsayilan=0.0)

        raf = giris_al("Raf konumu", zorunlu=False)
        aciklama = giris_al("Açıklama", zorunlu=False)

        # Tedarikçi seç
        tedarikciler = db.execute("SELECT id, ad FROM tedarikciler ORDER BY ad").fetchall()
        tedarikci_id = None
        if tedarikciler:
            secenekler = ["(Yok)"] + [r["ad"] for r in tedarikciler]
            print(alt_baslik("Tedarikçi"))
            idx = secim_al("Tedarikçi seçin", secenekler, varsayilan=1)
            if idx > 0:
                tedarikci_id = tedarikciler[idx - 1]["id"]

        db.execute("""
            INSERT INTO urunler
              (kod, ad, kategori_id, tedarikci_id, barkod, birim,
               alis_fiyati, satis_fiyati, kdv_orani, stok_miktari,
               minimum_stok, maksimum_stok, raf_konumu, aciklama)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (kod, ad, kategori_id, tedarikci_id, barkod or None, birim,
              alis_fiyati, satis_fiyati, kdv_orani, ilk_stok,
              minimum_stok, maksimum_stok if maksimum_stok > 0 else None,
              raf or None, aciklama or None))

        urun_id = db.execute("SELECT id FROM urunler WHERE kod=?", (kod,)).fetchone()["id"]

        if ilk_stok > 0:
            db.execute("""
                INSERT INTO stok_hareketleri
                  (urun_id, hareket_tipi, miktar, onceki_stok, sonraki_stok,
                   birim_fiyat, toplam_tutar, aciklama, yapan)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (urun_id, "giris", ilk_stok, 0, ilk_stok,
                  alis_fiyati, ilk_stok * alis_fiyati,
                  "Başlangıç stoğu", "Sistem"))

        print(basari(f"Ürün '{ad}' (Kod: {kod}) başarıyla eklendi."))
    devam_et()


def urun_listele(kategori_id: int = None, sadece_aktif: bool = True,
                 arama: str = ""):
    print(baslik("ÜRÜN LİSTESİ"))

    kosullar = ["1=1"]
    parametreler = []
    if sadece_aktif:
        kosullar.append("u.aktif=1")
    if kategori_id:
        kosullar.append("u.kategori_id=?")
        parametreler.append(kategori_id)
    if arama:
        kosullar.append("(u.ad LIKE ? OR u.kod LIKE ? OR u.barkod LIKE ?)")
        parametreler.extend([f"%{arama}%", f"%{arama}%", f"%{arama}%"])

    sql = f"""
        SELECT u.id, u.kod, u.ad, k.ad as kategori,
               u.birim, u.stok_miktari, u.minimum_stok,
               u.alis_fiyati, u.satis_fiyati, u.aktif
        FROM urunler u
        LEFT JOIN kategoriler k ON k.id=u.kategori_id
        WHERE {' AND '.join(kosullar)}
        ORDER BY u.ad
    """
    with veritabani() as db:
        rows = db.execute(sql, parametreler).fetchall()

    if not rows:
        print(bilgi("Ürün bulunamadı."))
        devam_et()
        return

    satirlar = []
    renkler = []
    for r in rows:
        stok = r["stok_miktari"]
        min_stok = r["minimum_stok"]
        durum = "✓" if r["aktif"] else "✗"

        if stok <= 0:
            renk = Renk.KIRMIZI
            stok_str = renkli(f"{stok:.2f}", Renk.KIRMIZI, Renk.KALIN)
        elif stok < min_stok:
            renk = Renk.SARI
            stok_str = renkli(f"{stok:.2f}", Renk.SARI, Renk.KALIN)
        else:
            renk = ""
            stok_str = f"{stok:.2f}"

        satirlar.append([
            r["id"], r["kod"], r["ad"], r["kategori"] or "-",
            r["birim"], stok_str,
            para_formatla(r["alis_fiyati"]),
            para_formatla(r["satis_fiyati"]),
            durum
        ])
        renkler.append(renk)

    tablo_yazdir(
        ["ID", "Kod", "Ürün Adı", "Kategori", "Birim", "Stok",
         "Alış", "Satış", "Aktif"],
        satirlar, renkler
    )
    print(renkli("  ⚠ Sarı: Minimum stok altı   ✗ Kırmızı: Stok tükendi", Renk.GRI))
    devam_et()


def urun_ara():
    print(baslik("ÜRÜN ARA"))
    arama = giris_al("Aranacak kelime (ad, kod veya barkod)")
    urun_listele(arama=arama, sadece_aktif=False)


def urun_detay(urun_id: int = None):
    print(baslik("ÜRÜN DETAYI"))
    if urun_id is None:
        urun_id = int(giris_al("Ürün ID"))

    with veritabani() as db:
        u = db.execute("""
            SELECT u.*, k.ad as kategori_adi, t.ad as tedarikci_adi
            FROM urunler u
            LEFT JOIN kategoriler k ON k.id=u.kategori_id
            LEFT JOIN tedarikciler t ON t.id=u.tedarikci_id
            WHERE u.id=?
        """, (urun_id,)).fetchone()

        if not u:
            print(hata("Ürün bulunamadı!"))
            devam_et()
            return

        print(f"\n  {renkli('Kod:', Renk.CYAN)}            {u['kod']}")
        print(f"  {renkli('Ad:', Renk.CYAN)}             {u['ad']}")
        print(f"  {renkli('Barkod:', Renk.CYAN)}         {u['barkod'] or '-'}")
        print(f"  {renkli('Kategori:', Renk.CYAN)}       {u['kategori_adi'] or '-'}")
        print(f"  {renkli('Tedarikçi:', Renk.CYAN)}      {u['tedarikci_adi'] or '-'}")
        print(f"  {renkli('Birim:', Renk.CYAN)}          {u['birim']}")
        print(f"  {renkli('Raf Konumu:', Renk.CYAN)}     {u['raf_konumu'] or '-'}")
        print(f"  {renkli('Alış Fiyatı:', Renk.CYAN)}   {para_formatla(u['alis_fiyati'])}")
        print(f"  {renkli('Satış Fiyatı:', Renk.CYAN)}  {para_formatla(u['satis_fiyati'])}")
        print(f"  {renkli('KDV Oranı:', Renk.CYAN)}     %{u['kdv_orani']:.0f}")
        stok = u["stok_miktari"]
        min_s = u["minimum_stok"]
        stok_renk = Renk.KIRMIZI if stok <= 0 else (Renk.SARI if stok < min_s else Renk.YESIL)
        print(f"  {renkli('Mevcut Stok:', Renk.CYAN)}   {renkli(f'{stok:.2f} {u[\"birim\"]}', stok_renk, Renk.KALIN)}")
        print(f"  {renkli('Minimum Stok:', Renk.CYAN)}  {u['minimum_stok']:.2f}")
        print(f"  {renkli('Maksimum Stok:', Renk.CYAN)} {u['maksimum_stok'] or 'Sınırsız'}")
        print(f"  {renkli('Durum:', Renk.CYAN)}         {'Aktif' if u['aktif'] else renkli('Pasif', Renk.KIRMIZI)}")
        print(f"  {renkli('Açıklama:', Renk.CYAN)}      {u['aciklama'] or '-'}")
        print(f"  {renkli('Eklenme:', Renk.CYAN)}       {tarih_formatla(u['olusturma_tarihi'])}")

        # Son 5 hareket
        hareketler = db.execute("""
            SELECT hareket_tipi, miktar, sonraki_stok, tarih, aciklama
            FROM stok_hareketleri WHERE urun_id=?
            ORDER BY tarih DESC LIMIT 5
        """, (urun_id,)).fetchall()

        if hareketler:
            print(alt_baslik("Son 5 Stok Hareketi"))
            tablo_yazdir(
                ["Tip", "Miktar", "Yeni Stok", "Tarih", "Açıklama"],
                [[h["hareket_tipi"].upper(), h["miktar"],
                  h["sonraki_stok"], tarih_formatla(h["tarih"]),
                  h["aciklama"] or "-"]
                 for h in hareketler]
            )
    devam_et()


def urun_guncelle():
    print(baslik("ÜRÜN GÜNCELLE"))
    urun_id = int(giris_al("Güncellenecek ürün ID"))

    with veritabani() as db:
        u = db.execute("SELECT * FROM urunler WHERE id=?", (urun_id,)).fetchone()
        if not u:
            print(hata("Ürün bulunamadı!"))
            devam_et()
            return

        print(bilgi(f"Güncellenecek ürün: {u['ad']} ({u['kod']})"))
        print(bilgi("Değiştirmek istemediğiniz alanlar için Enter'a basın.\n"))

        ad = giris_al("Ürün adı", varsayilan=u["ad"])
        barkod = giris_al("Barkod", varsayilan=u["barkod"] or "", zorunlu=False)
        alis_fiyati  = sayi_giris_al("Alış fiyatı", varsayilan=u["alis_fiyati"])
        satis_fiyati = sayi_giris_al("Satış fiyatı", varsayilan=u["satis_fiyati"])
        kdv_orani    = sayi_giris_al("KDV oranı (%)", varsayilan=u["kdv_orani"])
        minimum_stok = sayi_giris_al("Minimum stok", varsayilan=u["minimum_stok"])
        raf = giris_al("Raf konumu", varsayilan=u["raf_konumu"] or "", zorunlu=False)
        aciklama = giris_al("Açıklama", varsayilan=u["aciklama"] or "", zorunlu=False)
        aktif = evet_hayir("Ürün aktif mi?", varsayilan=bool(u["aktif"]))

        db.execute("""
            UPDATE urunler SET
              ad=?, barkod=?, alis_fiyati=?, satis_fiyati=?, kdv_orani=?,
              minimum_stok=?, raf_konumu=?, aciklama=?, aktif=?,
              guncelleme_tarihi=CURRENT_TIMESTAMP
            WHERE id=?
        """, (ad, barkod or None, alis_fiyati, satis_fiyati, kdv_orani,
              minimum_stok, raf or None, aciklama or None,
              1 if aktif else 0, urun_id))

        print(basari(f"Ürün '{ad}' güncellendi."))
    devam_et()


def urun_sil():
    print(baslik("ÜRÜN SİL (PASİF YAP)"))
    print(uyari("Ürünler fiziksel olarak silinmez, pasif duruma alınır."))
    urun_id = int(giris_al("Pasif yapılacak ürün ID"))

    with veritabani() as db:
        u = db.execute("SELECT id, ad, kod FROM urunler WHERE id=?", (urun_id,)).fetchone()
        if not u:
            print(hata("Ürün bulunamadı!"))
        elif evet_hayir(f"'{u['ad']}' ürününü pasif yapmak istiyor musunuz?", False):
            db.execute("UPDATE urunler SET aktif=0 WHERE id=?", (urun_id,))
            print(basari("Ürün pasif duruma alındı."))
        else:
            print(bilgi("İşlem iptal edildi."))
    devam_et()


def urun_menusu():
    while True:
        print(baslik("ÜRÜN YÖNETİMİ"))
        print(f"  {renkli('1', Renk.SARI)}) Tüm Ürünleri Listele")
        print(f"  {renkli('2', Renk.SARI)}) Ürün Ara")
        print(f"  {renkli('3', Renk.SARI)}) Ürün Detayı")
        print(f"  {renkli('4', Renk.SARI)}) Yeni Ürün Ekle")
        print(f"  {renkli('5', Renk.SARI)}) Ürün Güncelle")
        print(f"  {renkli('6', Renk.SARI)}) Ürün Pasif Yap")
        print(f"  {renkli('7', Renk.SARI)}) Kategori Yönetimi")
        print(f"  {renkli('0', Renk.KIRMIZI)}) Ana Menüye Dön")
        secim = input(renkli("\n  Seçiminiz: ", Renk.BEYAZ)).strip()

        if secim == "1":
            urun_listele()
        elif secim == "2":
            urun_ara()
        elif secim == "3":
            urun_detay()
        elif secim == "4":
            urun_ekle()
        elif secim == "5":
            urun_guncelle()
        elif secim == "6":
            urun_sil()
        elif secim == "7":
            kategori_menusu()
        elif secim == "0":
            break
        else:
            print(hata("Geçersiz seçim!"))
