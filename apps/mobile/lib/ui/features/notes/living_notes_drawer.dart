import 'package:flutter/material.dart';
import '../../../core/services/haptic_feedback_service.dart';
import '../../core/app_theme.dart';
import 'prerequisite_ladder_widget.dart';

class LivingNoteData {
  final String nodeId;
  final String title;
  final int level;
  final String oneSentenceIntuition;
  final List<PrerequisiteStepItem> prerequisites;
  final List<String> solutionRecipe;
  final String miniExercisePrompt;
  final String miniExerciseAnswer;
  final String miniExerciseExplanation;
  final String deepInsight;

  const LivingNoteData({
    required this.nodeId,
    required this.title,
    this.level = 0,
    required this.oneSentenceIntuition,
    required this.prerequisites,
    required this.solutionRecipe,
    required this.miniExercisePrompt,
    required this.miniExerciseAnswer,
    required this.miniExerciseExplanation,
    required this.deepInsight,
  });

  static final Map<String, LivingNoteData> catalog = {
    'N01': const LivingNoteData(
      nodeId: 'N01',
      title: 'Negatif Sayılar ve Sayı Doğrusu',
      level: 0,
      oneSentenceIntuition: 'Negatif sayı borç veya sayı doğrusunda sıfırın soluna doğru atılan adımdır.',
      prerequisites: [
        PrerequisiteStepItem(nodeId: 'N01', title: 'Negatif Sayılar'),
      ],
      solutionRecipe: [
        'Sayı doğrusunda başlangıç noktasını belirle.',
        'İşarete göre yön seç: artı sağa, eksi sola ilerletir.',
        'Birim kadar ilerle ve ulaştığın konumu işaretle.',
      ],
      miniExercisePrompt: '-3 + (-4) işleminin sonucu kaçtır?',
      miniExerciseAnswer: '-7',
      miniExerciseExplanation: 'Sıfırdan 3 birim sola, ardından 4 birim daha sola gidilince -7 konumuna varılır.',
      deepInsight: 'Eksinin eksi ile çarpımı, yönün iki kez ters çevrilmesiyle pozitif yönü verir.',
    ),
    'N04': const LivingNoteData(
      nodeId: 'N04',
      title: '1. Dereceden Lineer Denklem',
      level: 1,
      oneSentenceIntuition: 'Denklem dengede bir terazidir; x\'i yalnız bırakmak için iki kefeye aynı işlem uygulanır.',
      prerequisites: [
        PrerequisiteStepItem(nodeId: 'N01', title: 'Negatif Sayılar'),
        PrerequisiteStepItem(nodeId: 'N04', title: 'Lineer Denklem'),
      ],
      solutionRecipe: [
        'Bilinen sayıları bir tarafa, x\'li terimleri diğer tarafa topla.',
        'Karşıya geçen sayının işaretini zıt işarete dönüştür.',
        'Her iki tarafı x\'in katsayısına bölerek x\'i yalnız bırak.',
      ],
      miniExercisePrompt: '2x + 4 = 10 ise x kaçtır?',
      miniExerciseAnswer: '3',
      miniExerciseExplanation: '4 karşıya eksi geçer: 2x = 6. İki taraf 2\'ye bölünür: x = 3.',
      deepInsight: 'Cebirin temel yasası: Bir kefeye ne yaparsan diğer kefeye de aynısını yap.',
    ),
    'N15': const LivingNoteData(
      nodeId: 'N15',
      title: 'İkinci Dereceden Denklem Çözümü',
      level: 2,
      oneSentenceIntuition: 'İçinde x² olan bir denklemde amaç iki tane 1. dereceden denklem elde etmektir.',
      prerequisites: [
        PrerequisiteStepItem(nodeId: 'N01', title: 'Negatif Sayılar'),
        PrerequisiteStepItem(nodeId: 'N04', title: 'Lineer Denklem'),
        PrerequisiteStepItem(nodeId: 'N15', title: '2. Dereceden Denklem'),
      ],
      solutionRecipe: [
        'Tüm terimleri tek tarafa toplayarak sağ tarafı sıfıra eşitle: ax² + bx + c = 0.',
        'Sol tarafı çarpanlarına ayırarak çarpım biçimine getir: (x - p)(x - q) = 0.',
        'Sıfır Çarpım Kuralı ile her parantezi ayrı ayrı sıfıra eşitleyip kökleri bul.',
      ],
      miniExercisePrompt: '(x - 2)(x - 5) = 0 denkleminin pozitif kökleri toplamı kaçtır?',
      miniExerciseAnswer: '7',
      miniExerciseExplanation: 'Kökler x = 2 ve x = 5\'tir. Toplamları: 2 + 5 = 7.',
      deepInsight: 'Eğer çarpım sıfırsa, çarpanlardan en az biri sıfır olmak zorundadır.',
    ),
  };

  static LivingNoteData getNote(String nodeId) {
    return catalog[nodeId] ?? catalog.values.first;
  }
}

/// Living Notes Drawer (Bölüm 3 - Geriye Doğru Zincirlenmiş Yaşayan Ders Notları)
/// Renders 1-sentence intuition, clickable prerequisite ladder, 3-step recipe, and 10s mini-exercise.
class LivingNotesDrawer extends StatefulWidget {
  final String initialNodeId;
  final VoidCallback? onResumeSession;
  final ValueChanged<String>? onNoteVisited;

  const LivingNotesDrawer({
    super.key,
    required this.initialNodeId,
    this.onResumeSession,
    this.onNoteVisited,
  });

  static Future<void> show(
    BuildContext context, {
    required String nodeId,
    VoidCallback? onResumeSession,
    ValueChanged<String>? onNoteVisited,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.bgPrimary,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => FractionallySizedBox(
        heightFactor: 0.90,
        child: LivingNotesDrawer(
          initialNodeId: nodeId,
          onResumeSession: onResumeSession,
          onNoteVisited: onNoteVisited,
        ),
      ),
    );
  }

  @override
  State<LivingNotesDrawer> createState() => _LivingNotesDrawerState();
}

class _LivingNotesDrawerState extends State<LivingNotesDrawer> {
  late String _currentNodeId;
  late LivingNoteData _note;
  final TextEditingController _exerciseController = TextEditingController();
  bool? _isExerciseCorrect;
  String? _exerciseFeedback;

  @override
  void initState() {
    super.initState();
    _currentNodeId = widget.initialNodeId;
    _loadNote(_currentNodeId);
  }

  @override
  void didUpdateWidget(covariant LivingNotesDrawer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialNodeId != widget.initialNodeId) {
      _loadNote(widget.initialNodeId);
    }
  }

  void _loadNote(String nodeId) {
    setState(() {
      _currentNodeId = nodeId;
      _note = LivingNoteData.getNote(nodeId);
      _exerciseController.clear();
      _isExerciseCorrect = null;
      _exerciseFeedback = null;
    });
    widget.onNoteVisited?.call(nodeId);
  }

  @override
  void dispose() {
    _exerciseController.dispose();
    super.dispose();
  }

  void _submitExercise() {
    final input = _exerciseController.text.trim().toLowerCase().replaceAll(RegExp(r'\s+'), '');
    final expected = _note.miniExerciseAnswer.trim().toLowerCase().replaceAll(RegExp(r'\s+'), '');

    if (input.isEmpty) return;

    if (input == expected) {
      HapticFeedbackService().stepSuccess();
      setState(() {
        _isExerciseCorrect = true;
        _exerciseFeedback = 'Tebrikler! ${_note.miniExerciseExplanation}';
      });
    } else {
      HapticFeedbackService().stepError();
      setState(() {
        _isExerciseCorrect = false;
        _exerciseFeedback = 'Tekrar dene! İpucu: ${_note.oneSentenceIntuition}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const Key('living_notes_drawer'),
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 20),
      child: Column(
        children: [
          // Top Navigation Action Bar
          Row(
            children: [
              ElevatedButton.icon(
                key: const Key('resume_session_button'),
                onPressed: () {
                  HapticFeedbackService().selectionClick();
                  Navigator.pop(context);
                  widget.onResumeSession?.call();
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6366F1),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: const Icon(Icons.arrow_back_rounded, size: 16, color: Colors.white),
                label: const Text(
                  'Kaldığım Soruya Geri Dön',
                  style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.close_rounded, color: AppColors.textMuted),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Content Scroll Area
          Expanded(
            child: ListView(
              children: [
                // Note Title and Level Badge
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF38BDF8).withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        _note.nodeId,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF38BDF8),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _note.title,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 14),

                // 1-Sentence Core Intuition Banner
                Container(
                  key: const Key('note_intuition_banner'),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E1B4B).withValues(alpha: 0.8),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF818CF8).withValues(alpha: 0.4)),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.lightbulb_outline_rounded, color: Color(0xFFA5B4FC), size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          _note.oneSentenceIntuition,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFFE0E7FF),
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 14),

                // Prerequisite Ladder
                PrerequisiteLadderWidget(
                  chain: _note.prerequisites,
                  activeNodeId: _note.nodeId,
                  onSelectNode: (selectedNodeId) {
                    _loadNote(selectedNodeId);
                  },
                ),

                const SizedBox(height: 16),

                // 3-Step Actionable Solution Recipe
                const Text(
                  '3 Adımlı Çözüm Reçetesi',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF38BDF8),
                  ),
                ),
                const SizedBox(height: 8),
                ...List.generate(3, (index) {
                  return Container(
                    key: Key('note_recipe_step_$index'),
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    decoration: BoxDecoration(
                      color: AppColors.bgSurface,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFF334155)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        CircleAvatar(
                          radius: 10,
                          backgroundColor: const Color(0xFF38BDF8).withValues(alpha: 0.2),
                          child: Text(
                            '${index + 1}',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF38BDF8),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            _note.solutionRecipe[index],
                            style: const TextStyle(
                              fontSize: 13,
                              color: AppColors.textPrimary,
                              height: 1.35,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }),

                const SizedBox(height: 14),

                // 10-Second Embedded Mini-Exercise
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F172A),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.4)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.timer_outlined, size: 16, color: Color(0xFF10B981)),
                          SizedBox(width: 6),
                          Text(
                            '10 Saniyelik Mini-Alıştırma',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF10B981),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _note.miniExercisePrompt,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Expanded(
                            child: TextField(
                              key: const Key('mini_exercise_input'),
                              controller: _exerciseController,
                              style: const TextStyle(color: Colors.white, fontFamily: 'monospace'),
                              decoration: InputDecoration(
                                hintText: 'Cevap...',
                                hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                                filled: true,
                                fillColor: const Color(0xFF1E293B),
                                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                              ),
                              onSubmitted: (_) => _submitExercise(),
                            ),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton(
                            key: const Key('mini_exercise_submit'),
                            onPressed: _submitExercise,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.accentCorrect,
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                            child: const Text('Kontrol Et', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                      if (_exerciseFeedback != null) ...[
                        const SizedBox(height: 10),
                        Text(
                          _exerciseFeedback!,
                          key: const Key('mini_exercise_feedback'),
                          style: TextStyle(
                            fontSize: 12.5,
                            fontWeight: FontWeight.w600,
                            color: _isExerciseCorrect == true ? AppColors.accentCorrect : AppColors.accentWarning,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
