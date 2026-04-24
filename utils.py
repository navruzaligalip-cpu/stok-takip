"""Terminal renklendirme, tablo çizimi ve genel yardımcı fonksiyonlar."""
import os
import sys
from datetime import datetime
from typing import Any, List, Optional


# ── ANSI renk kodları ──────────────────────────────────────────────────────────
class Renk:
    SIFIRLA   = "\033[0m"
    KALIN     = "\033[1m"
    KIRMIZI   = "\033[91m"
    YESIL     = "\033[92m"
    SARI      = "\033[93m"
    MAVI      = "\033[94m"
    MAGENTA   = "\033[95m"
    CYAN      = "\033[96m"
    BEYAZ     = "\033[97m"
    GRI       = "\033[90m"
    BG_KIRMIZI = "\033[41m"
    BG_YESIL  = "\033[42m"


def renkli(metin: str, *kodlar: str) -> str:
    return "".join(kodlar) + metin + Renk.SIFIRLA


def basari(metin: str) -> str:
    return renkli(f"✓ {metin}", Renk.YESIL, Renk.KALIN)


def hata(metin: str) -> str:
    return renkli(f"✗ {metin}", Renk.KIRMIZI, Renk.KALIN)


def uyari(metin: str) -> str:
    return renkli(f"⚠ {metin}", Renk.SARI, Renk.KALIN)


def bilgi(metin: str) -> str:
    return renkli(f"ℹ {metin}", Renk.CYAN)


def baslik(metin: str, genislik: int = 60) -> str:
    cizgi = "═" * genislik
    return (
        renkli(f"\n{cizgi}", Renk.MAVI) + "\n"
        + renkli(f"  {metin}", Renk.MAVI, Renk.KALIN) + "\n"
        + renkli(f"{cizgi}", Renk.MAVI)
    )


def alt_baslik(metin: str) -> str:
    return renkli(f"\n── {metin} ──", Renk.CYAN, Renk.KALIN)


def ekrani_temizle():
    os.system("cls" if os.name == "nt" else "clear")


# ── Tablo çizici ───────────────────────────────────────────────────────────────
def tablo_yazdir(basliklar: List[str], satirlar: List[List[Any]],
                 renkler: Optional[List[str]] = None):
    """Verilen başlık ve satırları hizalı tablo olarak yazdırır."""
    if not satirlar:
        print(bilgi("Kayıt bulunamadı."))
        return

    sutun_genislikleri = [len(str(b)) for b in basliklar]
    for satir in satirlar:
        for i, hucre in enumerate(satir):
            sutun_genislikleri[i] = max(sutun_genislikleri[i], len(str(hucre)))

    ayrac = "┼".join("─" * (g + 2) for g in sutun_genislikleri)
    ust   = "┬".join("─" * (g + 2) for g in sutun_genislikleri)
    alt   = "┴".join("─" * (g + 2) for g in sutun_genislikleri)

    print(renkli("┌" + ust + "┐", Renk.GRI))
    baslik_satiri = "│".join(
        renkli(f" {str(b).center(g)} ", Renk.KALIN, Renk.CYAN)
        for b, g in zip(basliklar, sutun_genislikleri)
    )
    print(f"│{baslik_satiri}│")
    print(renkli("├" + ayrac + "┤", Renk.GRI))

    for idx, satir in enumerate(satirlar):
        renk = (renkler[idx] if renkler and idx < len(renkler) else "")
        hücreler = "│".join(
            (renk + f" {str(h).ljust(g)} " + Renk.SIFIRLA)
            for h, g in zip(satir, sutun_genislikleri)
        )
        print(f"│{hücreler}│")

    print(renkli("└" + alt + "┘", Renk.GRI))
    print(renkli(f"  Toplam: {len(satirlar)} kayıt", Renk.GRI))


# ── Giriş yardımcıları ────────────────────────────────────────────────────────
def giris_al(soru: str, varsayilan: str = "", zorunlu: bool = True) -> str:
    """Kullanıcıdan metin girdisi alır."""
    while True:
        if varsayilan:
            gosterilen = f"{soru} [{varsayilan}]: "
        else:
            gosterilen = f"{soru}: "

        cevap = input(renkli(gosterilen, Renk.BEYAZ)).strip()
        if not cevap and varsayilan:
            return varsayilan
        if cevap or not zorunlu:
            return cevap
        print(hata("Bu alan boş bırakılamaz!"))


def sayi_giris_al(soru: str, varsayilan: Optional[float] = None,
                  minimum: float = 0, maksimum: float = float("inf"),
                  tam_sayi: bool = False) -> float:
    """Kullanıcıdan sayısal giriş alır, doğrulama yapar."""
    while True:
        vs_goster = f" [{varsayilan}]" if varsayilan is not None else ""
        cevap = input(renkli(f"{soru}{vs_goster}: ", Renk.BEYAZ)).strip()
        if not cevap and varsayilan is not None:
            return varsayilan
        try:
            deger = int(cevap) if tam_sayi else float(cevap)
            if minimum <= deger <= maksimum:
                return deger
            print(hata(f"Değer {minimum} ile {maksimum} arasında olmalıdır."))
        except ValueError:
            print(hata("Geçerli bir sayı giriniz!"))


def evet_hayir(soru: str, varsayilan: bool = True) -> bool:
    """E/H sorusu sorar."""
    secenekler = "[E/h]" if varsayilan else "[e/H]"
    while True:
        cevap = input(renkli(f"{soru} {secenekler}: ", Renk.SARI)).strip().lower()
        if not cevap:
            return varsayilan
        if cevap in ("e", "evet", "y", "yes"):
            return True
        if cevap in ("h", "hayır", "hayir", "n", "no"):
            return False
        print(hata("Lütfen E veya H giriniz."))


def secim_al(soru: str, secenekler: List[str],
             varsayilan: Optional[int] = None) -> int:
    """Numaralı listeden seçim yaptırır, seçilen indeksi döner."""
    for i, s in enumerate(secenekler, 1):
        print(f"  {renkli(str(i), Renk.SARI, Renk.KALIN)}) {s}")
    while True:
        vs = f" [{varsayilan}]" if varsayilan is not None else ""
        cevap = input(renkli(f"{soru}{vs}: ", Renk.BEYAZ)).strip()
        if not cevap and varsayilan is not None:
            return varsayilan - 1
        try:
            idx = int(cevap) - 1
            if 0 <= idx < len(secenekler):
                return idx
            print(hata(f"1 ile {len(secenekler)} arasında bir sayı giriniz."))
        except ValueError:
            print(hata("Geçersiz seçim!"))


def devam_et():
    input(renkli("\n  Devam etmek için Enter'a basınız...", Renk.GRI))


# ── Para biçimi ────────────────────────────────────────────────────────────────
def para_formatla(tutar: float, birim: str = "TL") -> str:
    return f"{tutar:,.2f} {birim}"


# ── Tarih ─────────────────────────────────────────────────────────────────────
def simdi() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def tarih_formatla(tarih_str: Optional[str]) -> str:
    if not tarih_str:
        return "-"
    try:
        dt = datetime.strptime(tarih_str[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return tarih_str


def kod_uret(on_ek: str, mevcut_kodlar: List[str]) -> str:
    """Benzersiz bir ürün kodu üretir."""
    for i in range(1, 99999):
        aday = f"{on_ek}{i:05d}"
        if aday not in mevcut_kodlar:
            return aday
    return f"{on_ek}99999"
