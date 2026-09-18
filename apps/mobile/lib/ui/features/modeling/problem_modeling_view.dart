import 'package:flutter/material.dart';
import 'widgets/motion_diagram_widget.dart';
import 'widgets/mixture_vessel_widget.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../../data/services/engine_api_service.dart';

enum ModelingStageType {
  variable,
  equation,
  solve,
}

/// Sokratik Modelleme Problemi Veri Modeli
class ProblemPreset {
  final String id;
  final String category;
  final String title;
  final String storyText;
  final String targetUnknown;
  final String schematicType; // 'MOTION_TIMELINE' | 'MIXTURE_VESSEL' | 'NONE'
  final String canonicalVar;
  final List<String> acceptableVars;
  final List<String> validEquationSnippets;
  final List<String> validSolutions;

  const ProblemPreset({
    required this.id,
    required this.category,
    required this.title,
    required this.storyText,
    required this.targetUnknown,
    required this.schematicType,
    required this.canonicalVar,
    required this.acceptableVars,
    required this.validEquationSnippets,
    required this.validSolutions,
  });
}

const List<ProblemPreset> kDefaultProblemPresets = [
  ProblemPreset(
    id: 'PROB_AGE_01',
    category: 'Yaş Problemleri',
    title: 'Babanın ve Oğlunun Yaşları',
    storyText:
        'Bir babanın bugünkü yaşı, oğlunun bugünkü yaşının 3 katıdır. 5 yıl sonra babanın ve oğlunun yaşları toplamı 50 olacaktır. Oğlunun bugünkü yaşı kaçtır?',
    targetUnknown: 'Oğlunun bugünkü yaşı',
    schematicType: 'NONE',
    canonicalVar: 'x',
    acceptableVars: ['x', 'y', 'a', 'o'],
    validEquationSnippets: ['(x + 5) + (3*x + 5) = 50', '(x+5)+(3x+5)=50', '4*x + 10 = 50', '4x + 10 = 50', '4x+10=50', '3*x + x + 10 = 50', '50'],
    validSolutions: ['10', 'x = 10', 'x=10'],
  ),
  ProblemPreset(
    id: 'PROB_MOTION_01',
    category: 'Hareket Problemleri',
    title: 'Karşıt Yönlü İki Aracın Karşılaşması',
    storyText:
        'A ve B şehirleri arasındaki mesafe 400 kilometredir. Saatteki hızları 60 km ve 40 km olan iki otomobil aynı anda birbirlerine doğru yola çıkıyor. Kaç saat sonra karşılaşırlar?',
    targetUnknown: 'Araçların karşılaşma süresi (saat)',
    schematicType: 'MOTION_TIMELINE',
    canonicalVar: 't',
    acceptableVars: ['t', 'x', 's'],
    validEquationSnippets: ['(60 + 40) * t = 400', '(60+40)*t=400', '(60 + 40) * t = 400', '100 * t = 400', '100t = 400', '100t=400', '60*t + 40*t = 400', '400'],
    validSolutions: ['4', 't = 4', 't=4', '4 saat'],
  ),
  ProblemPreset(
    id: 'PROB_MIXTURE_01',
    category: 'Karışım Problemleri',
    title: 'Tuzlu Su Karışımlarının Birleşimi',
    storyText:
        'Tuz oranı %20 olan 40 litre tuzlu su ile tuz oranı %50 olan 60 litre tuzlu su karıştırılıyor. Yeni karışımın tuz oranı yüzde kaç olur?',
    targetUnknown: 'Yeni karışımın tuz yüzdesi (%)',
    schematicType: 'MIXTURE_VESSEL',
    canonicalVar: 'x',
    acceptableVars: ['x', 'y', 'c', 'p'],
    validEquationSnippets: ['40 * 20 + 60 * 50 = (40 + 60) * x', '40*20+60*50=100*x', '800 + 3000 = 100 * x', '100 * x = 3800', '100x = 3800', '3800'],
    validSolutions: ['38', 'x = 38', 'x=38', '%38'],
  ),
  ProblemPreset(
    id: 'PROB_WORK_01',
    category: 'İşçi Problemleri',
    title: 'Birlikte Çalışan İşçiler',
    storyText:
        'Bir işi Ali tek başına 6 günde, Veli ise 12 günde bitirebilmektedir. İkisi birlikte çalışırlarsa aynı işi kaç günde bitirirler?',
    targetUnknown: 'İşin birlikte bitirilme süresi (gün)',
    schematicType: 'NONE',
    canonicalVar: 't',
    acceptableVars: ['t', 'x', 'g'],
    validEquationSnippets: ['1/6 + 1/12 = 1/t', '1/6+1/12=1/t', '3/12 = 1/t', '1/4 = 1/t', 't/6 + t/12 = 1'],
    validSolutions: ['4', 't = 4', 't=4', '4 gün'],
  ),
  ProblemPreset(
    id: 'PROB_PERCENT_01',
    category: 'Yüzde & Kâr-Zarar',
    title: 'Ardışık Zam ve İndirim',
    storyText:
        'Bir mağaza bir cekete maliyet üzerinden %30 kâr koyarak satış fiyatı belirliyor. Sezon sonunda bu satış fiyatı üzerinden %20 indirim uyguluyor. Mağazanın net kâr oranı yüzde kaçtır?',
    targetUnknown: 'Net kâr oranı (%)',
    schematicType: 'NONE',
    canonicalVar: 'k',
    acceptableVars: ['k', 'x', 'y', 'p'],
    validEquationSnippets: ['100 * 1.30 * 0.80 = 100 + k', '100*1.30*0.80=100+k', '104 = 100 + k', '1.30 * 0.80 = 1 + k/100', '104'],
    validSolutions: ['4', 'k = 4', 'k=4', '%4'],
  ),
  ProblemPreset(
    id: 'PROB_OPTIMIZATION_01',
    category: 'Optimizasyon',
    title: 'Bahçe Alanını Maksimum Yapma',
    storyText:
        'Çevresi 60 metre olan dikdörtgen biçimindeki bir bahçenin alanının en büyük olması için bir kenar uzunluğu kaç metre olmalıdır?',
    targetUnknown: 'Maksimum alan veren kenar uzunluğu (metre)',
    schematicType: 'NONE',
    canonicalVar: 'x',
    acceptableVars: ['x', 'a', 'k'],
    validEquationSnippets: ['x * (30 - x) = 225', 'x*(30-x)=225', '-x**2 + 30*x = 225', '-x^2 + 30*x = 225', '225', 'x = 15'],
    validSolutions: ['15', 'x = 15', 'x=15', '15 metre'],
  ),
];

/// Sokratik Problem Modelleme Ekranı (Word Problems & Modeling).
/// Öğrenciyi 3 aşamalı iskele (Scaffold) ile yönlendirir:
/// 1. Değişkeni Belirle -> 2. Eşitliği Kur -> 3. Çöz ve Gerçek Hayat Uygunluğunu Sına.
class ProblemModelingView extends StatefulWidget {
  final String? problemId;
  final String? category;
  final String? title;
  final String? storyText;
  final String? targetUnknown;
  final String? schematicType; // 'MOTION_TIMELINE' | 'MIXTURE_VESSEL' | 'NONE'
  final EngineApiService? apiService;
  final String? studentId;

  const ProblemModelingView({
    super.key,
    this.problemId,
    this.category,
    this.title,
    this.storyText,
    this.targetUnknown,
    this.schematicType,
    this.apiService,
    this.studentId,
  });

  @override
  State<ProblemModelingView> createState() => _ProblemModelingViewState();
}

class _ProblemModelingViewState extends State<ProblemModelingView> {
  late int _activePresetIndex;
  ModelingStageType _currentStage = ModelingStageType.variable;
  final TextEditingController _inputController = TextEditingController();
  bool _isSubmitting = false;

  String? _socraticFeedback;
  String? _detectedBugId;
  bool _isAllCompleted = false;

  // Aşama 1 için kaydedilen değişken adı
  String _selectedVar = 'x';

  @override
  void initState() {
    super.initState();
    // Gelen parametreye göre en uygun başlangıç indeksini bul
    int initialIdx = 0;
    if (widget.problemId != null) {
      final idx = kDefaultProblemPresets.indexWhere((p) => p.id == widget.problemId);
      if (idx != -1) initialIdx = idx;
    } else if (widget.schematicType == 'MOTION_TIMELINE') {
      initialIdx = 1;
    } else if (widget.schematicType == 'MIXTURE_VESSEL') {
      initialIdx = 2;
    }
    _activePresetIndex = initialIdx;
  }

  ProblemPreset get _currentPreset {
    final base = kDefaultProblemPresets[_activePresetIndex];
    return ProblemPreset(
      id: widget.problemId ?? base.id,
      category: widget.category ?? base.category,
      title: widget.title ?? base.title,
      storyText: widget.storyText ?? base.storyText,
      targetUnknown: widget.targetUnknown ?? base.targetUnknown,
      schematicType: widget.schematicType ?? base.schematicType,
      canonicalVar: base.canonicalVar,
      acceptableVars: base.acceptableVars,
      validEquationSnippets: base.validEquationSnippets,
      validSolutions: base.validSolutions,
    );
  }

  void _switchPreset(int index) {
    if (index == _activePresetIndex) return;
    HapticFeedbackService().selectionClick();
    setState(() {
      _activePresetIndex = index;
      _currentStage = ModelingStageType.variable;
      _selectedVar = kDefaultProblemPresets[index].canonicalVar;
      _socraticFeedback = null;
      _detectedBugId = null;
      _isAllCompleted = false;
      _inputController.clear();
    });
  }

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  Future<void> _submitCurrentStep() async {
    final input = _inputController.text.trim();
    if (input.isEmpty || _isSubmitting) return;

    final preset = _currentPreset;

    setState(() {
      _detectedBugId = null;
      _socraticFeedback = null;
      _isSubmitting = true;
    });

    // 1. Canlı API İstemcisi Entegrasyonu (Hedef 9)
    if (widget.apiService != null) {
      try {
        final stageStr = _currentStage == ModelingStageType.variable
            ? 'STAGE_1_VARIABLE'
            : (_currentStage == ModelingStageType.equation
                ? 'STAGE_2_EQUATION'
                : 'STAGE_3_SOLVE');

        final resp = await widget.apiService!.submitModelingScaffoldStep(
          sessionId: 'modeling_sess_${preset.id}',
          problemId: preset.id,
          stage: stageStr,
          studentInput: input,
          variableName: _selectedVar,
          studentId: widget.studentId ?? 'STU-MODEL-01',
        );

        final bool isValid = resp['is_valid'] == true;
        final bool stageCompleted = resp['stage_completed'] == true;
        final String feedback = (resp['socratic_feedback'] as String?) ?? '';
        final Map<String, dynamic>? detectedBug = resp['detected_bug'] as Map<String, dynamic>?;
        final String? bugId = detectedBug?['bug_id'] as String?;

        if (mounted) {
          if (isValid) {
            HapticFeedbackService().stepSuccess();
            setState(() {
              _socraticFeedback = feedback;
              _detectedBugId = null;
              if (_currentStage == ModelingStageType.variable) {
                _selectedVar = input.toLowerCase().contains(preset.canonicalVar.toLowerCase())
                    ? preset.canonicalVar
                    : input.trim();
                _currentStage = ModelingStageType.equation;
              } else if (_currentStage == ModelingStageType.equation) {
                _currentStage = ModelingStageType.solve;
              } else if (_currentStage == ModelingStageType.solve && stageCompleted) {
                _isAllCompleted = true;
              }
              _inputController.clear();
              _isSubmitting = false;
            });
            return;
          } else {
            HapticFeedbackService().stepError();
            setState(() {
              _socraticFeedback = feedback;
              _detectedBugId = bugId;
              _isSubmitting = false;
            });
            return;
          }
        }
      } catch (_) {
        // API hatasında kesintisiz çevrimdışı fallback'e geç
      }
    }

    // 2. Çevrimdışı / Yerel İskele Değerlendirmesi (Fallback)
    _executeOfflineStepEvaluation(input, preset);
  }

  void _executeOfflineStepEvaluation(String input, ProblemPreset preset) {
    if (_currentStage == ModelingStageType.variable) {
      // Aşama 1: Değişken Tanımla
      final clean = input.toLowerCase();
      bool isMatch = false;
      for (final v in preset.acceptableVars) {
        if (clean.contains(v)) {
          isMatch = true;
          _selectedVar = v;
          break;
        }
      }

      if (isMatch) {
        HapticFeedbackService().stepSuccess();
        setState(() {
          _socraticFeedback =
              'Harika bir başlangıç! "$_selectedVar" değişkenini "${preset.targetUnknown}" olarak belirledik. Şimdi eşitliği kuralım.';
          _currentStage = ModelingStageType.equation;
          _inputController.clear();
          _isSubmitting = false;
        });
      } else {
        HapticFeedbackService().stepError();
        setState(() {
          _socraticFeedback =
              'Seçtiğin değişken anlaşılamadı. Lütfen ${preset.canonicalVar} gibi tek bir cebirsel harf belirle.';
          _isSubmitting = false;
        });
      }
    } else if (_currentStage == ModelingStageType.equation) {
      // Aşama 2: Eşitliği Kur (Buggy Rules & Algebraic Equivalence)
      final clean = input.replaceAll(' ', '');

      // 1. Buggy Rule Kontrolleri
      if (input.contains('x + 5 = 2y') || clean.contains('x+5=2y') || input.contains('tekbirkisiyeyasartisi')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-01';
          _socraticFeedback =
              'Zaman herkes için eşit akar. Yıllar eklendiğinde denklemdeki her iki kişinin de yaşına aynı süre eklenmelidir: x + 5 = 2*(y + 5).';
          _isSubmitting = false;
        });
      } else if (input.contains('v1/v2 = t1/t2') || input.contains('v1/v2=t1/t2')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-02';
          _socraticFeedback =
              'Hız ile zaman doğru orantılı değil, ters orantılıdır! Sabit yolda hız arttıkça süre azalır: v1 * t1 = v2 * t2.';
          _isSubmitting = false;
        });
      } else if (input.contains('(60+40)/2') || input.contains('vort = 50') || input.contains('(60 + 40)/2')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-03';
          _socraticFeedback =
              'Ortalama hız hızların aritmetik ortalaması değildir! Toplam Yol / Toplam Zaman (harmonik ortalama) formülünü uygula.';
          _isSubmitting = false;
        });
      } else if (input.contains('1.20*0.80 = 1') || input.contains('1.20*0.80=1')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-04';
          _socraticFeedback =
              'Yüzde artış ve azalış birbirini sıfırlamaz! %20 zam ve %20 indirim: 1.20 * 0.80 = 0.96 (%4 zarar) olur.';
          _isSubmitting = false;
        });
      } else if (input.contains('tuz/su') || input.contains('yuzde = tuz/su')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-05';
          _socraticFeedback =
              'Karışım yüzdesi saf madde / su değil, Saf Madde / Toplam Karışım Hacmi oranıyla hesaplanır.';
          _isSubmitting = false;
        });
      } else if (input.contains('6 + 12 = 18') || input.contains('6+12=18') || input.contains('6 + 3 = 9') || input.contains('6+3=9')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-06';
          _socraticFeedback =
              'İki işçi birlikte çalışırken süreler toplanmaz, iş yapma kapasiteleri toplanır: 1/t1 + 1/t2 = 1/t_birlikte.';
          _isSubmitting = false;
        });
      } else if (input.contains('(v1-v2)*t') || input.contains('(60 - 40) * t = 400') || input.contains('(60-40)*t=400')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-07';
          _socraticFeedback =
              'Karşıt yönlü hareket eden araçlar birbirine yaklaşır; hızları toplanmalıdır: (v1 + v2) * t = Mesafe.';
          _isSubmitting = false;
        });
      } else if (input.contains('kar = satis * yuzde') || input.contains('satis * yuzde')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-08';
          _socraticFeedback =
              'Aksi belirtilmedikçe kâr marjı satış fiyatı üzerinden değil, maliyet tabanı üzerinden hesaplanır.';
          _isSubmitting = false;
        });
      } else if (input.contains('60 * 20') || input.contains('60*20')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-09';
          _socraticFeedback =
              'Birim uyuşmazlığı: Hız saatte km (km/h) olarak verilmişken süre dakika alınamaz; dakikayı 60\'a bölerek saate dönüştür.';
          _isSubmitting = false;
        });
      }
      // 2. Geçerli Denklem Kontrolü
      else {
        bool isValid = false;
        for (final snip in preset.validEquationSnippets) {
          if (clean.contains(snip.replaceAll(' ', '')) || input.contains(snip)) {
            isValid = true;
            break;
          }
        }

        // Genel eşitlik kabulü (örneğin eşitlik ve ana sayılar içeriyorsa)
        if (!isValid && input.contains('=')) {
          if (preset.id == 'PROB_AGE_01' && input.contains('50')) isValid = true;
          if (preset.id == 'PROB_MOTION_01' && (input.contains('400') || input.contains('100'))) isValid = true;
          if (preset.id == 'PROB_MIXTURE_01' && (input.contains('3800') || input.contains('100'))) isValid = true;
          if (preset.id == 'PROB_WORK_01' && (input.contains('1/t') || input.contains('1/6'))) isValid = true;
          if (preset.id == 'PROB_PERCENT_01' && (input.contains('100') || input.contains('104'))) isValid = true;
          if (preset.id == 'PROB_OPTIMIZATION_01' && (input.contains('225') || input.contains('15'))) isValid = true;
        }

        if (isValid) {
          HapticFeedbackService().stepSuccess();
          setState(() {
            _socraticFeedback =
                'Mükemmel modelleme! Matematiksel eşitliğin problemi tam olarak modelliyor. Şimdi denklemi adım adım çözelim.';
            _currentStage = ModelingStageType.solve;
            _inputController.clear();
            _isSubmitting = false;
          });
        } else {
          HapticFeedbackService().stepError();
          setState(() {
            _socraticFeedback =
                'Kurduğun eşitlik problemdeki verilerle tam uyuşmuyor. Değerleri ve bağıntıları tekrar kontrol et.';
            _isSubmitting = false;
          });
        }
      }
    } else if (_currentStage == ModelingStageType.solve) {
      // Aşama 3: Çöz ve Reel Dünya Doğrulaması (Zero Leakage)
      if (input.contains('-')) {
        HapticFeedbackService().stepError();
        setState(() {
          _detectedBugId = 'BUG-PROB-10';
          _socraticFeedback =
              'Gerçek hayatta yaş, hız, uzunluk veya zaman negatif olamaz. Lütfen pozitif kökü bul.';
          _isSubmitting = false;
        });
      } else {
        bool isCorrect = false;
        for (final sol in preset.validSolutions) {
          if (input.trim() == sol || input.replaceAll(' ', '').contains(sol.replaceAll(' ', ''))) {
            isCorrect = true;
            break;
          }
        }

        if (isCorrect) {
          HapticFeedbackService().stepSuccess();
          setState(() {
            _isAllCompleted = true;
            _socraticFeedback =
                'Tebrikler! Problemi 3 aşamalı modelleyip doğru ve gerçek hayata uygun çözüme ulaştın.';
            _isSubmitting = false;
          });
        } else {
          // Zero Leakage: Doğru kök asla söylenmez
          HapticFeedbackService().stepError();
          setState(() {
            _socraticFeedback =
                'İşlemlerde bir hata görünüyor. Bilinen sabit terimleri bir tarafa, bilinmeyenleri diğer tarafa toplayıp sadeleştir.';
            _isSubmitting = false;
          });
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final preset = _currentPreset;

    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: widget.apiService != null
                      ? Colors.greenAccent.withValues(alpha: 0.15)
                      : Colors.white10,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: widget.apiService != null
                        ? Colors.greenAccent.withValues(alpha: 0.5)
                        : Colors.white24,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      widget.apiService != null ? Icons.cloud_done : Icons.cloud_off,
                      size: 12,
                      color: widget.apiService != null ? Colors.greenAccent : Colors.white54,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      widget.apiService != null ? 'Canlı API' : 'Çevrimdışı',
                      style: TextStyle(
                        color: widget.apiService != null ? Colors.greenAccent : Colors.white54,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.amberAccent.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    preset.category,
                    style: const TextStyle(color: Colors.amberAccent, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    preset.title,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 2),
            const Text(
              '3 Aşamalı Sokratik Modelleme İskelesi',
              style: TextStyle(color: Colors.white54, fontSize: 11),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 0. Problem Preset Seçici Yatay Çubuk
            _buildPresetSelector(),
            const SizedBox(height: 16),

            // 1. Problem Hikayesi Kartı
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.menu_book, color: Colors.amberAccent, size: 18),
                      SizedBox(width: 8),
                      Text(
                        'Problem Metni',
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    preset.storyText,
                    style: const TextStyle(color: Colors.white70, fontSize: 13, height: 1.4),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.amberAccent.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.help_outline, color: Colors.amberAccent, size: 16),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            'Hedef: ${preset.targetUnknown}',
                            style: const TextStyle(color: Colors.amberAccent, fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // 2. Dinamik Şematik Görselleştirici (Opsiyonel)
            if (preset.schematicType == 'MOTION_TIMELINE')
              const MotionDiagramWidget()
            else if (preset.schematicType == 'MIXTURE_VESSEL')
              const MixtureVesselWidget(),

            if (preset.schematicType != 'NONE') const SizedBox(height: 16),

            // 3. Aşama İlerleme Göstergesi (Scaffold Stepper)
            _buildStepper(),
            const SizedBox(height: 16),

            // 4. Aktif Aşama Kartı
            _buildActiveStageCard(preset),
            const SizedBox(height: 16),

            // 5. Sokratik Geri Bildirim veya Hata Teşhis Kartı
            if (_socraticFeedback != null) _buildFeedbackCard(),

            if (_isAllCompleted) _buildCompletionCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildPresetSelector() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: List.generate(kDefaultProblemPresets.length, (idx) {
          final p = kDefaultProblemPresets[idx];
          final isSelected = idx == _activePresetIndex;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              key: Key('preset_chip_${p.id}'),
              label: Text(p.category),
              selected: isSelected,
              selectedColor: const Color(0xFF38BDF8).withValues(alpha: 0.3),
              backgroundColor: const Color(0xFF161B22),
              labelStyle: TextStyle(
                color: isSelected ? const Color(0xFF38BDF8) : Colors.white60,
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
              side: BorderSide(
                color: isSelected ? const Color(0xFF38BDF8) : Colors.white12,
              ),
              onSelected: (_) => _switchPreset(idx),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildStepper() {
    return Row(
      children: [
        _buildStepBadge(1, 'Değişken', _currentStage.index >= 0, _currentStage == ModelingStageType.variable),
        Expanded(child: Container(height: 2, color: _currentStage.index >= 1 ? Colors.greenAccent : Colors.white12)),
        _buildStepBadge(2, 'Eşitlik', _currentStage.index >= 1, _currentStage == ModelingStageType.equation),
        Expanded(child: Container(height: 2, color: _currentStage.index >= 2 ? Colors.greenAccent : Colors.white12)),
        _buildStepBadge(3, 'Çözüm', _currentStage.index >= 2, _currentStage == ModelingStageType.solve),
      ],
    );
  }

  Widget _buildStepBadge(int num, String label, bool isDoneOrActive, bool isActive) {
    Color bg = isDoneOrActive ? (isActive ? Colors.cyanAccent : Colors.greenAccent) : Colors.white12;
    Color fg = isDoneOrActive ? Colors.black : Colors.white54;

    return Column(
      children: [
        CircleAvatar(
          radius: 12,
          backgroundColor: bg,
          child: Text('$num', style: TextStyle(color: fg, fontSize: 11, fontWeight: FontWeight.bold)),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: isActive ? Colors.cyanAccent : Colors.white54,
            fontSize: 10,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ],
    );
  }

  Widget _buildActiveStageCard(ProblemPreset preset) {
    String stageTitle = '';
    String stagePrompt = '';
    String hintText = '';

    if (_currentStage == ModelingStageType.variable) {
      stageTitle = 'Aşama 1: Bilinmeyeni Tanımla';
      stagePrompt = 'Hangi büyüklüğe "${preset.canonicalVar}" demeliyiz?';
      hintText = 'Örn: ${preset.canonicalVar} = ${preset.targetUnknown.toLowerCase()}';
    } else if (_currentStage == ModelingStageType.equation) {
      stageTitle = 'Aşama 2: Eşitliği Kur';
      stagePrompt = 'Metindeki verileri birbirine bağlayan denklem nedir?';
      hintText = 'Örn: ${preset.validEquationSnippets.first}';
    } else {
      stageTitle = 'Aşama 3: Çöz ve Doğrula';
      stagePrompt = 'Denklemi çözerek sonucu girin (Zero-Leakage & Gerçek Hayat Kısıtı):';
      hintText = 'Örn: ${preset.canonicalVar} = ${preset.validSolutions.first}';
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(stageTitle, style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 14)),
          const SizedBox(height: 6),
          Text(stagePrompt, style: const TextStyle(color: Colors.white, fontSize: 12)),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  key: const Key('modeling_input_field'),
                  controller: _inputController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: hintText,
                    hintStyle: const TextStyle(color: Colors.white24, fontSize: 12),
                    filled: true,
                    fillColor: Colors.black26,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                key: const Key('modeling_submit_button'),
                onPressed: (_isAllCompleted || _isSubmitting) ? null : _submitCurrentStep,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyanAccent,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                      )
                    : const Text('Onayla', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackCard() {
    final bool isBug = _detectedBugId != null;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isBug ? Colors.redAccent.withValues(alpha: 0.15) : Colors.greenAccent.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isBug ? Colors.redAccent.withValues(alpha: 0.5) : Colors.greenAccent.withValues(alpha: 0.5),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isBug ? Icons.warning_amber_rounded : Icons.check_circle_outline,
                color: isBug ? Colors.redAccent : Colors.greenAccent,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                isBug ? 'Bilişsel Yanılgı: $_detectedBugId' : 'Sokratik Rehber',
                style: TextStyle(
                  color: isBug ? Colors.redAccent : Colors.greenAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            _socraticFeedback!,
            style: const TextStyle(color: Colors.white, fontSize: 12, height: 1.3),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletionCard() {
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.amberAccent.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amberAccent.withValues(alpha: 0.6)),
      ),
      child: Row(
        children: const [
          Icon(Icons.emoji_events, color: Colors.amberAccent, size: 28),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Modelleme Başarıyla Tamamlandı!',
                  style: TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 14),
                ),
                SizedBox(height: 2),
                Text(
                  'Soyut problemi değişken ve denkleme dönüştürdün, gerçek hayat kısıtlarıyla çözümü doğruladın.',
                  style: TextStyle(color: Colors.white70, fontSize: 11),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
