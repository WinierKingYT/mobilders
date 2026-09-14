import 'package:flutter/material.dart';
import 'widgets/motion_diagram_widget.dart';
import 'widgets/mixture_vessel_widget.dart';

enum ModelingStageType {
  variable,
  equation,
  solve,
}

/// Sokratik Problem Modelleme Ekranı (Word Problems & Modeling).
/// Öğrenciyi 3 aşamalı iskele (Scaffold) ile yönlendirir:
/// 1. Değişkeni Belirle -> 2. Eşitliği Kur -> 3. Çöz ve Gerçek Hayat Uygunluğunu Sına.
class ProblemModelingView extends StatefulWidget {
  final String problemId;
  final String category;
  final String title;
  final String storyText;
  final String targetUnknown;
  final String schematicType; // 'MOTION_TIMELINE' | 'MIXTURE_VESSEL' | 'NONE'

  const ProblemModelingView({
    super.key,
    this.problemId = 'PROB_AGE_01',
    this.category = 'Yaş Problemleri',
    this.title = 'Babanın ve Oğlunun Yaşları',
    this.storyText =
        'Bir babanın bugünkü yaşı, oğlunun bugünkü yaşının 3 katıdır. 5 yıl sonra babanın ve oğlunun yaşları toplamı 50 olacaktır. Oğlunun bugünkü yaşı kaçtır?',
    this.targetUnknown = 'Oğlunun bugünkü yaşı',
    this.schematicType = 'NONE',
  });

  @override
  State<ProblemModelingView> createState() => _ProblemModelingViewState();
}

class _ProblemModelingViewState extends State<ProblemModelingView> {
  ModelingStageType _currentStage = ModelingStageType.variable;
  final TextEditingController _inputController = TextEditingController();

  String? _socraticFeedback;
  String? _detectedBugId;
  bool _isStageCompleted = false;
  bool _isAllCompleted = false;

  // Aşama 1 için kaydedilen değişken adı
  String _selectedVar = 'x';

  @override
  void dispose() {
    _inputController.dispose();
    super.dispose();
  }

  void _submitCurrentStep() {
    final input = _inputController.text.trim();
    if (input.isEmpty) return;

    setState(() {
      _detectedBugId = null;
      _socraticFeedback = null;
    });

    if (_currentStage == ModelingStageType.variable) {
      // Aşama 1: Değişken Tanımla
      final clean = input.toLowerCase();
      if (clean.contains('x') || clean.contains('t') || clean.contains('y') || clean.contains('a')) {
        setState(() {
          _selectedVar = clean.replaceAll('=', '').replaceAll(' ', '').substring(0, 1);
          _socraticFeedback =
              'Harika bir başlangıç! "$_selectedVar" değişkenini "${widget.targetUnknown}" olarak belirledik. Şimdi eşitliği kuralım.';
          _currentStage = ModelingStageType.equation;
          _inputController.clear();
        });
      } else {
        setState(() {
          _socraticFeedback =
              'Seçtiğin değişken anlaşılamadı. Lütfen x veya t gibi tek bir cebirsel harf belirle.';
        });
      }
    } else if (_currentStage == ModelingStageType.equation) {
      // Aşama 2: Eşitliği Kur
      if (input.contains('x + 5 = 2y') || input.contains('x+5=2y') || input.contains('tekbirkisiyeyasartisi')) {
        setState(() {
          _detectedBugId = 'BUG-PROB-01';
          _socraticFeedback =
              'Zaman herkes için eşit akar. Yıllar eklendiğinde denklemdeki her iki kişinin de yaşına aynı süre eklenmelidir: x + 5 = 2*(y + 5).';
        });
      } else if (input.contains('=') && (input.contains('50') || input.contains('400') || input.contains('100') || input.contains('t'))) {
        setState(() {
          _socraticFeedback =
              'Mükemmel modelleme! Matematiksel eşitliğin problemi tam olarak modelliyor. Şimdi denklemi adım adım çözelim.';
          _currentStage = ModelingStageType.solve;
          _inputController.clear();
        });
      } else {
        setState(() {
          _socraticFeedback =
              'Kurduğun eşitlik problemdeki verilerle tam uyuşmuyor. Toplamları ve geçen yılları tekrar kontrol et.';
        });
      }
    } else if (_currentStage == ModelingStageType.solve) {
      // Aşama 3: Çöz ve Reel Dünya Doğrulaması
      if (input.contains('-')) {
        setState(() {
          _detectedBugId = 'BUG-PROB-10';
          _socraticFeedback =
              'Gerçek hayatta yaş, hız veya zaman negatif olamaz. Lütfen pozitif kökü bul.';
        });
      } else if (input.contains('10') || input.contains('4') || input.contains('38') || input.contains('15')) {
        setState(() {
          _isAllCompleted = true;
          _socraticFeedback =
              'Tebrikler! Problemi 3 aşamalı modelleyip doğru ve gerçek hayata uygun çözüme ulaştın.';
        });
      } else {
        // Zero Leakage: Doğru kök asla söylenmez
        setState(() {
          _socraticFeedback =
              'İşlemlerde bir hata görünüyor. Sabit terimleri karşıya geçirip her iki tarafı x\'in katsayısına böl.';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
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
                    widget.category,
                    style: const TextStyle(color: Colors.amberAccent, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  widget.title,
                  style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
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
                    widget.storyText,
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
                            'Hedef: ${widget.targetUnknown}',
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
            if (widget.schematicType == 'MOTION_TIMELINE')
              const MotionDiagramWidget()
            else if (widget.schematicType == 'MIXTURE_VESSEL')
              const MixtureVesselWidget(),

            if (widget.schematicType != 'NONE') const SizedBox(height: 16),

            // 3. Aşama İlerleme Göstergesi (Scaffold Stepper)
            _buildStepper(),
            const SizedBox(height: 16),

            // 4. Aktif Aşama Kartı
            _buildActiveStageCard(),
            const SizedBox(height: 16),

            // 5. Sokratik Geri Bildirim veya Hata Teşhis Kartı
            if (_socraticFeedback != null) _buildFeedbackCard(),

            if (_isAllCompleted) _buildCompletionCard(),
          ],
        ),
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

  Widget _buildActiveStageCard() {
    String stageTitle = '';
    String stagePrompt = '';
    String hintText = '';

    if (_currentStage == ModelingStageType.variable) {
      stageTitle = 'Aşama 1: Bilinmeyeni Tanımla';
      stagePrompt = 'Hangi büyüklüğe "x" demeliyiz?';
      hintText = 'Örn: x = oğlun bugünkü yaşı';
    } else if (_currentStage == ModelingStageType.equation) {
      stageTitle = 'Aşama 2: Eşitliği Kur';
      stagePrompt = 'Metindeki verileri birbirine bağlayan denklem nedir?';
      hintText = 'Örn: (x + 5) + (3*x + 5) = 50';
    } else {
      stageTitle = 'Aşama 3: Çöz ve Doğrula';
      stagePrompt = 'Denklemi çözerek sonucu girin (Zero-Leakage & Gerçek Hayat Kısıtı):';
      hintText = 'Örn: x = 10';
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
                onPressed: _isAllCompleted ? null : _submitCurrentStep,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyanAccent,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: const Text('Onayla', style: TextStyle(fontWeight: FontWeight.bold)),
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
