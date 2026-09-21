"""
Explorable Prerequisite Notes Repository (Yaşayan Ders Notları Motoru).
Bölüm 3 - Geriye Doğru Zincirlenmiş Yaşayan Ders Notları.
Provides:
- 1-Sentence Core Intuition ("one_sentence_intuition")
- Clickable Prerequisite Chain ("prerequisites")
- 3-Step Actionable Solution Recipe ("solution_recipe")
- 10-Second Embedded Mini-Exercise ("mini_exercise")
- Acyclic DAG guarantee and topological backward traversal.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field
import sympy as sp


class MiniExercise(BaseModel):
    prompt: str
    expected_answer: str
    explanation: str


class ExplorableNoteCard(BaseModel):
    node_id: str
    title: str
    level: int = 0
    one_sentence_intuition: str
    prerequisites: List[str] = Field(default_factory=list)
    solution_recipe: List[str] = Field(..., min_length=3, max_length=3)
    mini_exercise: MiniExercise
    deep_insight: str


class ExplorableNotesRepository:
    """
    Catalog and backward traversal engine for living prerequisite notes.
    """

    def __init__(self):
        self._notes: Dict[str, ExplorableNoteCard] = {}
        self._build_catalog()
        self.validate_dag_acyclic()

    def _build_catalog(self) -> None:
        cards = [
            # N01: Negatif Sayılar & Sayı Doğrusu
            ExplorableNoteCard(
                node_id="N01",
                title="Negatif Sayılar ve Sayı Doğrusu",
                level=0,
                one_sentence_intuition="Negatif sayı borç veya sayı doğrusunda sıfırın soluna doğru atılan adımdır.",
                prerequisites=[],
                solution_recipe=[
                    "Sayı doğrusunda başlangıç noktasını belirle.",
                    "İşarete göre yön seç: artı sağa, eksi sola ilerletir.",
                    "Birim kadar ilerle ve ulaştığın konumu işaretle.",
                ],
                mini_exercise=MiniExercise(
                    prompt="-3 + (-4) işleminin sonucu kaçtır?",
                    expected_answer="-7",
                    explanation="Sıfırdan 3 birim sola, ardından 4 birim daha sola gidilince -7 konumuna ulaşılır.",
                ),
                deep_insight="Eksinin eksi ile çarpımı, yönün iki kez ters çevrilmesiyle pozitif yönü verir.",
            ),

            # N02: Dağılma Özelliği & Parantez Açma
            ExplorableNoteCard(
                node_id="N02",
                title="Dağılma Özelliği ve Parantez Açma",
                level=0,
                one_sentence_intuition="Parantezin dışındaki çarpan, içerideki her bir terimin eşit hakkıdır.",
                prerequisites=["N01"],
                solution_recipe=[
                    "Parantezin dışındaki ortak çarpanı ve işaretini belirle.",
                    "Dıştaki çarpanı parantez içindeki her bir terimle sırayla çarp.",
                    "Elde edilen terimleri işaret kurallarını koruyarak yan yana yaz.",
                ],
                mini_exercise=MiniExercise(
                    prompt="2(x + 5) ifadesinin açılımı nedir?",
                    expected_answer="2x+10",
                    explanation="2 çarpanı hem x hem de 5 ile çarpılır: 2*x + 2*5 = 2x + 10.",
                ),
                deep_insight="Dağılma kuralı cebirdeki parantez kilitlerini açan anahtardır.",
            ),

            # N03: Benzer Terimleri Birleştirme
            ExplorableNoteCard(
                node_id="N03",
                title="Benzer Terimleri Birleştirme",
                level=0,
                one_sentence_intuition="Sadece aynı değişkene ve aynı üsse sahip terimler kendi aralarında toplanabilir.",
                prerequisites=["N01"],
                solution_recipe=[
                    "Aynı harfe ve aynı kuvvete sahip benzer terimleri grupla.",
                    "Gruplanan terimlerin önündeki katsayıları topla veya çıkar.",
                    "Ortak değişkeni değiştirmeden yeni katsayının yanına yaz.",
                ],
                mini_exercise=MiniExercise(
                    prompt="4x + 3x ifadesinin en sade hali nedir?",
                    expected_answer="7x",
                    explanation="Katsayılar toplanır: (4 + 3)x = 7x.",
                ),
                deep_insight="Elma ile armut toplanamaz; x ile x² de aynı cins değildir.",
            ),

            # N04: 1. Dereceden Lineer Denklem
            ExplorableNoteCard(
                node_id="N04",
                title="1. Dereceden Lineer Denklem",
                level=1,
                one_sentence_intuition="Denklem dengede duran bir terazidir; x'i yalnız bırakmak için iki kefeye aynı işlem uygulanır.",
                prerequisites=["N01", "N02", "N03"],
                solution_recipe=[
                    "Bilinen sayıları eşitliğin bir tarafına, x'li terimleri diğer tarafına topla.",
                    "Karşıya geçen sayının işaretini zıt işarete dönüştür.",
                    "Eşitliğin her iki tarafını x'in katsayısına bölerek x'i yalnız bırak.",
                ],
                mini_exercise=MiniExercise(
                    prompt="2x + 4 = 10 ise x kaçtır?",
                    expected_answer="3",
                    explanation="4 karşıya eksi geçer: 2x = 6. Her iki taraf 2'ye bölünür: x = 3.",
                ),
                deep_insight="Cebirin temel yasası: Bir kefeye ne yaparsan diğer kefeye de aynısını yap.",
            ),

            # N05: İki Kare Farkı Özdeşliği
            ExplorableNoteCard(
                node_id="N05",
                title="İki Kare Farkı Özdeşliği",
                level=1,
                one_sentence_intuition="İki tam karenin farkı, bu sayıların farkı ile toplamının çarpımına eşittir.",
                prerequisites=["N02"],
                solution_recipe=[
                    "Her iki terimin karekökünü alarak tabanları belirle: a ve b.",
                    "Biri eksi biri artı iki çarpan parantezi oluştur: (a - b) ve (a + b).",
                    "İfadeyi bu iki parantezin çarpımı şeklinde yaz.",
                ],
                mini_exercise=MiniExercise(
                    prompt="x² - 16 ifadesinin çarpanlarına ayrılmış hali nedir?",
                    expected_answer="(x-4)(x+4)",
                    explanation="x'in karesi x², 4'ün karesi 16'dır: (x - 4)(x + 4).",
                ),
                deep_insight="Geometrik olarak büyük kareden küçük köşe karesi kesildiğinde kalan alan iki dikdörtgene bölünür.",
            ),

            # N06: Tam Kare Özdeşliği
            ExplorableNoteCard(
                node_id="N06",
                title="Tam Kare Özdeşliği",
                level=1,
                one_sentence_intuition="Toplamın karesi; birincinin karesi, çarpımlarının iki katı ve ikincinin karesidir.",
                prerequisites=["N02", "N03"],
                solution_recipe=[
                    "Birinci terimin karesini al: a².",
                    "Birinci ile ikincinin çarpımının 2 katını ortaya yaz: 2ab.",
                    "İkinci terimin karesini son terim olarak ekle: b².",
                ],
                mini_exercise=MiniExercise(
                    prompt="(x + 3)² açılımındaki sabit terim kaçtır?",
                    expected_answer="9",
                    explanation="Sabit terim ikinci terimin karesidir: 3² = 9.",
                ),
                deep_insight="Kenarı (a + b) olan karenin alanı bir büyük kare, bir küçük kare ve iki eş dikdörtgenden oluşur.",
            ),

            # N07: Ortak Çarpan Parantezi
            ExplorableNoteCard(
                node_id="N07",
                title="Ortak Çarpan Parantezi",
                level=1,
                one_sentence_intuition="Tüm terimlerde ortak bulunan parçayı parantez dışına çekerek ifadeyi sadeleştirmektir.",
                prerequisites=["N02"],
                solution_recipe=[
                    "Tüm terimlerdeki ortak sayı bölenini ve ortak harfleri tespit et.",
                    "En büyük ortak çarpanı parantezin soluna yaz.",
                    "Her terimi ortak çarpana bölerek kalanları parantezin içine yerleştir.",
                ],
                mini_exercise=MiniExercise(
                    prompt="3x + 6 ifadesinde ortak çarpan 3 dışarı alınınca parantez içi ne olur?",
                    expected_answer="x+2",
                    explanation="3x / 3 = x ve 6 / 3 = 2 olduğundan parantez içi (x + 2)'dir.",
                ),
                deep_insight="Dağılma özelliğinin tam tersi işlemidir; kilidi geri kilitlemek gibidir.",
            ),

            # N15: İkinci Dereceden Denklem Çözümü
            ExplorableNoteCard(
                node_id="N15",
                title="İkinci Dereceden Denklem Çözümü",
                level=2,
                one_sentence_intuition="İçinde x² olan bir denklemde amaç iki tane 1. dereceden denklem elde etmektir.",
                prerequisites=["N04", "N05", "N07"],
                solution_recipe=[
                    "Tüm terimleri tek tarafa toplayarak sağ tarafı sıfıra eşitle: ax² + bx + c = 0.",
                    "Sol tarafı çarpanlarına ayırarak çarpım biçimine getir: (x - p)(x - q) = 0.",
                    "Sıfır Çarpım Kuralı ile her parantezi ayrı ayrı sıfıra eşitleyip kökleri bul.",
                ],
                mini_exercise=MiniExercise(
                    prompt="(x - 2)(x - 5) = 0 denkleminin pozitif kökleri toplamı kaçtır?",
                    expected_answer="7",
                    explanation="Kökler x = 2 ve x = 5'tir. Toplamları: 2 + 5 = 7.",
                ),
                deep_insight="Eğer çarpım sıfırsa, çarpanlardan en az biri sıfır olmak zorundadır.",
            ),

            # N20: Parabol Tepe Noktası & Grafiği
            ExplorableNoteCard(
                node_id="N20",
                title="Parabol Tepe Noktası ve Grafiği",
                level=3,
                one_sentence_intuition="Parabol simetrik bir vadidir; tepe noktası vadi tabanıdır ve x = -b/(2a) simetri eksenidir.",
                prerequisites=["N15"],
                solution_recipe=[
                    "Tepe noktasının apsisini r = -b / (2a) formülüyle hesapla.",
                    "Bulduğun r değerini fonksiyonda yerine yazıp ordinatı k = f(r) olarak bul.",
                    "T(r, k) noktasını işaretle; a > 0 ise yukarı, a < 0 ise aşağı kollarla simetrik çiz.",
                ],
                mini_exercise=MiniExercise(
                    prompt="f(x) = x² - 4x + 5 parabolünün tepe noktası apsisi (r) kaçtır?",
                    expected_answer="2",
                    explanation="r = -(-4) / (2*1) = 4 / 2 = 2.",
                ),
                deep_insight="Parabolün simetri ekseni iki kökün tam aritmetik ortalamasıdır.",
            ),

            # TRIG01: Birim Çember ve Temel Oranlar
            ExplorableNoteCard(
                node_id="TRIG01",
                title="Birim Çember ve Temel Trigonometri",
                level=2,
                one_sentence_intuition="Birim çemberde cos yatay gölge, sin dikey gölgedir.",
                prerequisites=["N01"],
                solution_recipe=[
                    "Pozitif x ekseninden başlayarak açıyı saat yönünün tersine döndür.",
                    "Çember üzerindeki kesim noktasının apsisini cos, ordinatını sin olarak oku.",
                    "tan değerini sin / cos oranı olarak türet.",
                ],
                mini_exercise=MiniExercise(
                    prompt="sin(90°) değeri kaçtır?",
                    expected_answer="1",
                    explanation="90 derecede çember tepe noktası (0, 1)'dir; ordinat sin = 1'dir.",
                ),
                deep_insight="Trigonometri üçgenlerden değil, çember etrafındaki sonsuz dönüşten doğar.",
            ),

            # TRIG02: Trigonometrik Özdeşlikler
            ExplorableNoteCard(
                node_id="TRIG02",
                title="Trigonometrik Özdeşlikler ve Pisagor",
                level=3,
                one_sentence_intuition="Birim çemberdeki her nokta dik üçgen oluşturur, bu yüzden sin²(x) + cos²(x) daima 1'dir.",
                prerequisites=["TRIG01"],
                solution_recipe=[
                    "Tüm tan ve cot ifadelerini sin ve cos cinsine dönüştür.",
                    "sin²(x) + cos²(x) = 1 Pisagor özdeşliğini kullanarak terimleri sadeleştir.",
                    "Payda eşitleyip ortak paranteze alarak sadeleştirilmiş biçimi bul.",
                ],
                mini_exercise=MiniExercise(
                    prompt="1 - cos²(x) ifadesi neye eşittir?",
                    expected_answer="sin^2(x)",
                    explanation="sin²(x) + cos²(x) = 1 olduğundan 1 - cos²(x) = sin²(x) olur.",
                ),
                deep_insight="Tüm trigonometrik dönüşümler tek bir dik üçgen Pisagor bağıntısının kılık değiştirmiş halidir.",
            ),

            # CALC01: Limit Sezgisi ve Yaklaşım
            ExplorableNoteCard(
                node_id="CALC01",
                title="Limit Sezgisi ve Yaklaşım",
                level=3,
                one_sentence_intuition="Limit hedefe basmak değil; hedefe sonsuz yaklaştığında yolun nereye baktığını görmektir.",
                prerequisites=["N04"],
                solution_recipe=[
                    "Yaklaşılan x değerini fonksiyonda yerine doğrudan yaz.",
                    "0/0 belirsizliği çıkarsa çarpanlara ayırma veya eşlenikle belirsizliği yok et.",
                    "Sadeleşmiş ifadede değeri yerine yazıp limit sonucunu oku.",
                ],
                mini_exercise=MiniExercise(
                    prompt="x -> 3 iken (2x + 1) ifadesinin limiti kaçtır?",
                    expected_answer="7",
                    explanation="Doğrudan yerine koyma: 2(3) + 1 = 7.",
                ),
                deep_insight="Fonksiyon o noktada tanımlı olmasa veya delik olsa bile limit var olabilir.",
            ),

            # CALC02: Türevin Geometrik Anlamı
            ExplorableNoteCard(
                node_id="CALC02",
                title="Türevin Geometrik Anlamı ve Teğet Eğimi",
                level=4,
                one_sentence_intuition="Türev bir anlık fotoğrafın hız göstergesidir; eğrinin o noktadaki teğetinin eğimidir.",
                prerequisites=["CALC01"],
                solution_recipe=[
                    "Fonksiyonun türev alma kuralını uygulayarak f'(x) fonksiyonunu bul.",
                    "Verilen noktanın apsisini türevde yerine yazarak teğetin eğimini m = f'(x0) hesapla.",
                    "Eğimi teğet doğrusunun dikliği ve yönü olarak yorumla.",
                ],
                mini_exercise=MiniExercise(
                    prompt="f(x) = x² fonksiyonunun x = 3 noktasındaki türevi kaçtır?",
                    expected_answer="6",
                    explanation="f'(x) = 2x kuralından f'(3) = 2*3 = 6.",
                ),
                deep_insight="Kirişin iki ucunu birbirine sonsuz yaklaştırdığımızda kiriş teğete dönüşür.",
            ),

            # CALC03: Türev Çarpım Kuralı
            ExplorableNoteCard(
                node_id="CALC03",
                title="Çarpımın Türevi Kuralı",
                level=4,
                one_sentence_intuition="İki değişen kenarlı dikdörtgende alan değişimi u·v' + v·u' şeklinde iki yönden gelir.",
                prerequisites=["CALC02"],
                solution_recipe=[
                    "Çarpım durumundaki iki parçayı u(x) ve v(x) olarak belirle.",
                    "Her parçanın ayrı ayrı türevini hesapla: u'(x) ve v'(x).",
                    "(u·v)' = u'·v + u·v' formülünde yerine koy ve topla.",
                ],
                mini_exercise=MiniExercise(
                    prompt="u = x, v = x² ise (u*v)' türevinin x = 1 için değeri kaçtır?",
                    expected_answer="3",
                    explanation="u*v = x³ -> türevi 3x². x=1 için 3(1)² = 3.",
                ),
                deep_insight="Türev operatörü çarpma işlemi üzerine doğrudan dağılmaz; kenar büyüme dengesini korur.",
            ),

            # CALC04: Belirli İntegral ve Alan
            ExplorableNoteCard(
                node_id="CALC04",
                title="Belirli İntegral ve Alan Hesabı",
                level=5,
                one_sentence_intuition="İntegral sonsuz küçüklükteki şeritlerin alanlarını toplayarak eğrinin altındaki net alanı bulmaktır.",
                prerequisites=["CALC02"],
                solution_recipe=[
                    "İçerideki fonksiyonun belirsiz integralini (ters türevini) F(x) olarak bul.",
                    "Üst sınır b ve alt sınır a için F(b) ve F(a) değerlerini hesapla.",
                    "Kalkülüsün Temel Teoremi ile F(b) - F(a) farkını alarak net alanı bul.",
                ],
                mini_exercise=MiniExercise(
                    prompt="0'dan 2'ye x dx belirli integralinin sonucu kaçtır?",
                    expected_answer="2",
                    explanation="İlkel fonksiyon x²/2'dir. F(2) - F(0) = 4/2 - 0 = 2.",
                ),
                deep_insight="Türev eğriyi parçalara böler, integral ise o parçaları birleştirir; birbirinin tam tersidir.",
            ),
        ]

        for card in cards:
            self._notes[card.node_id] = card

    def get_note(self, node_id: str) -> Optional[ExplorableNoteCard]:
        return self._notes.get(node_id)

    def get_all_notes(self) -> List[ExplorableNoteCard]:
        return list(self._notes.values())

    def get_prerequisite_chain(self, node_id: str) -> List[ExplorableNoteCard]:
        """
        Traverses backwards from node_id down to root prerequisites in hierarchical order.
        Guaranteed to be topological and acyclic.
        """
        if node_id not in self._notes:
            return []

        visited: Set[str] = set()
        chain: List[ExplorableNoteCard] = []

        def dfs(curr_id: str, depth: int = 0):
            if depth > 50:
                return
            if curr_id in visited or curr_id not in self._notes:
                return
            visited.add(curr_id)
            curr_card = self._notes[curr_id]
            for prereq_id in curr_card.prerequisites:
                dfs(prereq_id, depth + 1)
            chain.append(curr_card)

        dfs(node_id, 0)
        return chain

    def verify_mini_exercise(self, node_id: str, user_answer: str) -> Tuple[bool, str]:
        card = self.get_note(node_id)
        if not card:
            return False, "Ders notu bulunamadı."

        if not user_answer or not isinstance(user_answer, str):
            return False, f"Lütfen bir cevap girin. İpucu: {card.one_sentence_intuition}"

        # DoS guard: limit user_answer length to 200 chars
        if len(user_answer) > 200:
            return False, "Cevap çok uzun. Lütfen daha kısa bir ifade girin."

        clean_user = user_answer.strip().replace(" ", "").lower()
        clean_exp = card.mini_exercise.expected_answer.strip().replace(" ", "").lower()

        if clean_user == clean_exp:
            return True, f"Tebrikler! {card.mini_exercise.explanation}"

        # Try CAS symbolic equivalence
        try:
            from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
            trans = standard_transformations + (implicit_multiplication_application,)
            lhs = parse_expr(clean_user, transformations=trans)
            rhs = parse_expr(clean_exp, transformations=trans)
            if sp.simplify(lhs - rhs) == 0:
                return True, f"Harika! Cebirsel olarak denk: {card.mini_exercise.explanation}"
        except Exception:
            pass

        return False, f"Tekrar dene! İpucu: {card.one_sentence_intuition}"

    def validate_dag_acyclic(self) -> bool:
        """
        Validates that all prerequisites exist and there are no cycles (DFS white/gray/black).
        """
        # 1. Existence check
        for nid, card in self._notes.items():
            for prereq in card.prerequisites:
                if prereq not in self._notes:
                    raise ValueError(f"Düğüm {nid} için tanımlı önkoşul {prereq} not kataloğunda bulunamadı!")

        # 2. Cycle check (DFS)
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {nid: WHITE for nid in self._notes}

        def dfs_cycle(u: str):
            colors[u] = GRAY
            for v in self._notes[u].prerequisites:
                if colors[v] == GRAY:
                    raise ValueError(f"Önkoşul zincirinde döngü tespit edildi: {u} -> {v}")
                if colors[v] == WHITE:
                    dfs_cycle(v)
            colors[u] = BLACK

        for nid in self._notes:
            if colors[nid] == WHITE:
                dfs_cycle(nid)

        return True
