# 📚 BÖLÜM 3: GERİYE DOĞRU ZİNCİRLENMİŞ YAŞAYAN DERS NOTLARI

Bu goal, statik PDF notlar yerine; tıklanabilir "Önkoşul Merdiveni", 1 cümlelik sezgi özeti, adım adım çözüm reçetesi ve 10 saniyelik mini-alıştırma içeren yaşayan ders kartlarını kurar.

---

## ⚡ ÇALIŞTIRILABİLİR /goal KOMUTU

```markdown
/goal Kişisel Öğrenme Motoru (PLE) projesinde Bölüm 3 "Geriye Doğru Zincirlenmiş Yaşayan Ders Notları (Explorable Prerequisite Notes)" paketini uçtan uca uygula ve doğrula:

1. Yaşayan Not Veri Modeli (Prerequisite Chain):
   - Her not kartı: 
     * 1 Cümlelik Temel Sezgi ("İçinde x² olan bir denklemde amaç iki tane 1. dereceden denklem elde etmektir").
     * Tıklanabilir Önkoşul Bağlantıları (Örn: 2. Dereceden Denklem -> 1. Dereceden Denklem -> Terazi Modeli -> Negatif Sayılar).
     * 3 Adımlı Net Çözüm Reçetesi.
     * 10 Saniyelik Gömülü Mini-Alıştırma Widget'ı.
2. In-Situ Geri Sarım ve Soruya Geri Dönüş:
   - Öğrenci lise sorusu çözerken önkoşul notuna indiğinde soru dondurulur; temeli kavradığında [⬅️ Kaldığım Soruya Geri Dön] ile kaldığı yerden devam eder.
3. Bilişsel Zaaf Defteri Entegrasyonu:
   - Ziyaret edilen önkoşul eksiklikleri öğrencinin zihinsel haritasında "Pekiştirilmesi Gereken Düğümler" listesine eklenir.
4. Mobil Arayüz (LivingNotesDrawer & ExplorableCardView):
   - Hero geçişleri ve akıcı önkoşul derinlik gezgini.
5. En az 25 yeni test ile not ağının bütünlüğünü ve döngüsüzlüğünü doğrula.
```

---

## 📋 Beklenen Teslimatlar
- `services/core-engine/engine/curriculum/explorable_notes_repository.py`
- `apps/mobile/lib/ui/features/notes/living_notes_drawer.dart`
- `apps/mobile/lib/ui/features/notes/prerequisite_ladder_widget.dart`
