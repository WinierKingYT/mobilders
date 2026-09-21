import 'package:flutter/material.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/mistake_vault_service.dart';
import 'package:personal_learning_engine/domain/models/twin_question_model.dart';


enum MistakeFilter { all, open, inRemediation, cured }

class MistakeAutopsyItem {
  final String id;
  final String bugId;
  final String nodeId;
  final String problem;
  final String offendingStep;
  final String correctPrinciple;
  final String status; // 'open', 'in_remediation', 'cured'
  final double stabilityDays;
  final bool isDue;

  const MistakeAutopsyItem({
    required this.id,
    required this.bugId,
    required this.nodeId,
    required this.problem,
    required this.offendingStep,
    required this.correctPrinciple,
    required this.status,
    required this.stabilityDays,
    this.isDue = true,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'bug_id': bugId,
        'node_id': nodeId,
        'problem': problem,
        'offending_step': offendingStep,
        'correct_principle': correctPrinciple,
        'status': status,
        'stability_days': stabilityDays,
        'is_due': isDue,
      };

  factory MistakeAutopsyItem.fromJson(Map<String, dynamic> json) {
    final rawStab = (json['stability_days'] as num?)?.toDouble() ?? 0.5;
    final safeStab = rawStab.isFinite && !rawStab.isNaN && rawStab >= 0.0 ? rawStab : 0.5;
    return MistakeAutopsyItem(
      id: json['id'] as String? ?? '',
      bugId: json['bug_id'] as String? ?? '',
      nodeId: json['node_id'] as String? ?? '',
      problem: json['problem'] as String? ?? '',
      offendingStep: json['offending_step'] as String? ?? '',
      correctPrinciple: json['correct_principle'] as String? ?? '',
      status: json['status'] as String? ?? 'open',
      stabilityDays: safeStab,
      isDue: json['is_due'] as bool? ?? true,
    );
  }
}

class MistakeAutopsyView extends StatefulWidget {
  final List<MistakeAutopsyItem> mistakes;
  final VoidCallback? onStartBossBattle;
  final ValueChanged<MistakeAutopsyItem>? onSelfCorrectionCompleted;
  final Future<void> Function(MistakeAutopsyItem item, String twinEquation)? onLaunchTwinPractice;
  final EngineApiService? apiService;

  const MistakeAutopsyView({
    super.key,
    required this.mistakes,
    this.onStartBossBattle,
    this.onSelfCorrectionCompleted,
    this.onLaunchTwinPractice,
    this.apiService,
  });

  @override
  State<MistakeAutopsyView> createState() => _MistakeAutopsyViewState();
}

class _MistakeAutopsyViewState extends State<MistakeAutopsyView> {
  MistakeFilter _filter = MistakeFilter.all;
  MistakeAutopsyItem? _activeSelfCorrectionItem;
  int _selfCorrectionStage = 1; // 1: Teşhis, 2: İlke, 3: Temiz Çözüm
  bool _isGeneratingTwin = false;
  TwinQuestionModel? _generatedTwin;

  void _resetSelfCorrection() {
    setState(() {
      _activeSelfCorrectionItem = null;
      _selfCorrectionStage = 1;
      _isGeneratingTwin = false;
      _generatedTwin = null;
    });
  }

  @override
  void didUpdateWidget(covariant MistakeAutopsyView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (_activeSelfCorrectionItem != null) {
      final stillExists = widget.mistakes.any((m) => m.id == _activeSelfCorrectionItem!.id);
      if (!stillExists) {
        _resetSelfCorrection();
      }
    }
  }

  List<MistakeAutopsyItem> get _filteredMistakes {
    switch (_filter) {
      case MistakeFilter.all:
        return widget.mistakes;
      case MistakeFilter.open:
        return widget.mistakes.where((m) => m.status == 'open').toList();
      case MistakeFilter.inRemediation:
        return widget.mistakes.where((m) => m.status == 'in_remediation').toList();
      case MistakeFilter.cured:
        return widget.mistakes.where((m) => m.status == 'cured').toList();
    }
  }

  int get _dueCount => widget.mistakes.where((m) => m.isDue && m.status != 'cured').length;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: const Key('mistake_vault_view'),
      appBar: AppBar(
        title: const Text("Bilişsel Hata Otopsisi Kasası"),
        backgroundColor: const Color(0xFF0F172A),
      ),
      backgroundColor: const Color(0xFF090D16),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Boss Battle Banner (shows if >= 3 due mistakes)
              if (_dueCount >= 3) _buildBossBattleBanner(),

              // 2. Stats Bar
              _buildStatsBar(),
              const SizedBox(height: 10),

              // 3. Filter Chips
              _buildFilterChips(),
              const SizedBox(height: 12),

              // 4. Interactive Self-Correction Flow Modal / Card (if active)
              if (_activeSelfCorrectionItem != null)
                _buildSelfCorrectionCard()
              else ...[
                // 5. Mistakes List
                if (widget.mistakes.isEmpty)
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 48.0, horizontal: 24.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: const Color(0xFF10B981).withValues(alpha: 0.1),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.verified_rounded,
                              color: Color(0xFF10B981),
                              size: 48,
                            ),
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            "Kayıtlı Bilişsel Hata Yok",
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            "Harika! Henüz tespit edilen kavram yanılgısı veya zihinsel zaaf bulunmuyor. Seanslarda karşılaştığınız hatalar otomatik olarak buraya kaydedilip tedavi edilecektir.",
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.white60, fontSize: 13, height: 1.4),
                          ),
                        ],
                      ),
                    ),
                  )
                else if (_filteredMistakes.isEmpty)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32.0),
                      child: Text(
                        "Bu filtre kategorisinde kayıtlı hata bulunmuyor.",
                        style: TextStyle(color: Colors.white54, fontSize: 14),
                      ),
                    ),
                  )
                else
                  ..._filteredMistakes.map(_buildMistakeCard),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBossBattleBanner() {
    return Container(
      key: const Key('boss_battle_banner'),
      margin: const EdgeInsets.only(bottom: 12.0),
      padding: const EdgeInsets.all(14.0),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF831843), Color(0xFF500724)],
        ),
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: Colors.redAccent.withValues(alpha: 0.6)),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber_rounded, color: Colors.amberAccent, size: 36),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "KAVRAM CANAVARI UYANDI!",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                Text(
                  "$_dueCount hata birikti. Boss Battle ile hafızanı sağlamlaştır!",
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
          ElevatedButton(
            key: const Key('btn_boss_battle'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.amberAccent,
              foregroundColor: Colors.black,
            ),
            onPressed: widget.onStartBossBattle,
            child: const Text("Meydan Oku", style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsBar() {
    final total = widget.mistakes.length;
    final cured = widget.mistakes.where((m) => m.status == 'cured').length;
    final rate = total == 0 ? 0 : ((cured / total) * 100).toInt();

    return Container(
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(10.0),
        border: Border.all(color: Colors.white12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _statCol("Toplam Hata", "$total", Colors.white),
          _statCol("Tekrar Bekleyen", "$_dueCount", Colors.orangeAccent),
          _statCol("Kür Edildi", "$cured", Colors.greenAccent),
          _statCol("Kür Oranı", "%$rate", Colors.cyanAccent),
        ],
      ),
    );
  }

  Widget _statCol(String label, String value, Color color) {
    return Column(
      children: [
        Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 16)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(color: Colors.white54, fontSize: 11)),
      ],
    );
  }

  Widget _buildFilterChips() {
    return Wrap(
      spacing: 8.0,
      children: [
        ChoiceChip(
          key: const Key('filter_all'),
          label: const Text("Tümü"),
          selected: _filter == MistakeFilter.all,
          onSelected: (val) => setState(() => _filter = MistakeFilter.all),
        ),
        ChoiceChip(
          key: const Key('filter_open'),
          label: const Text("Açık"),
          selected: _filter == MistakeFilter.open,
          onSelected: (val) => setState(() => _filter = MistakeFilter.open),
        ),
        ChoiceChip(
          key: const Key('filter_remediation'),
          label: const Text("Telafide"),
          selected: _filter == MistakeFilter.inRemediation,
          onSelected: (val) => setState(() => _filter = MistakeFilter.inRemediation),
        ),
        ChoiceChip(
          key: const Key('filter_cured'),
          label: const Text("Kür Edildi"),
          selected: _filter == MistakeFilter.cured,
          onSelected: (val) => setState(() => _filter = MistakeFilter.cured),
        ),
      ],
    );
  }

  Widget _buildMistakeCard(MistakeAutopsyItem item) {
    Color statusColor = Colors.redAccent;
    String statusText = "Açık Hata";
    if (item.status == 'in_remediation') {
      statusColor = Colors.orangeAccent;
      statusText = "Telafi Aşamasında";
    } else if (item.status == 'cured') {
      statusColor = Colors.greenAccent;
      statusText = "Kür Edildi (Usta)";
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      padding: const EdgeInsets.all(14.0),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: statusColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  item.bugId,
                  style: const TextStyle(
                    color: Colors.redAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
              Text(
                statusText,
                style: TextStyle(color: statusColor, fontSize: 12, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            item.problem,
            style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.black26,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.close, color: Colors.redAccent, size: 16),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    "Yapılan Hatalı Hamle: ${item.offendingStep}",
                    style: const TextStyle(
                      color: Colors.redAccent,
                      fontSize: 12,
                      decoration: TextDecoration.lineThrough,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 6),
          Row(
            children: [
              const Icon(Icons.check, color: Colors.greenAccent, size: 16),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  "Doğru Kural: ${item.correctPrinciple}",
                  style: const TextStyle(color: Colors.lightGreenAccent, fontSize: 12),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "FSRS Hafıza: ${item.stabilityDays.toStringAsFixed(1)} Gün",
                style: const TextStyle(color: Colors.white54, fontSize: 11),
              ),
              if (item.status != 'cured')
                ElevatedButton(
                  key: Key('btn_start_self_correction_${item.id}'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.cyanAccent,
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  ),
                  onPressed: () {
                    setState(() {
                      _activeSelfCorrectionItem = item;
                      _selfCorrectionStage = 1;
                    });
                  },
                  child: const Text("Hatayı Düzelt", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSelfCorrectionCard() {
    final item = _activeSelfCorrectionItem!;
    return Container(
      key: const Key('self_correction_flow'),
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: Colors.cyanAccent),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Kendi Hatasını Düzeltme: Aşama $_selfCorrectionStage/3",
                style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 14),
              ),
              IconButton(
                icon: const Icon(Icons.close, color: Colors.white54, size: 18),
                onPressed: _resetSelfCorrection,
              ),
            ],
          ),
          const Divider(color: Colors.white12),
          if (_selfCorrectionStage == 1) ...[
            const Text(
              "1. Aşama: Hatanı Teşhis Et",
              key: Key('stage_1_view'),
              style: TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 13),
            ),
            const SizedBox(height: 6),
            Text("Yazdığın adım: ${item.offendingStep}"),
            const SizedBox(height: 12),
            ElevatedButton(
              key: const Key('btn_stage_1_confirm'),
              onPressed: () => setState(() => _selfCorrectionStage = 2),
              child: const Text("Hatalı Kuralı Teşhis Ettim"),
            ),
          ] else if (_selfCorrectionStage == 2) ...[
            const Text(
              "2. Aşama: Doğru İlkeyi İfade Et",
              key: Key('stage_2_view'),
              style: TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 13),
            ),
            const SizedBox(height: 6),
            Text("Doğru kural: ${item.correctPrinciple}"),
            const SizedBox(height: 12),
            ElevatedButton(
              key: const Key('btn_stage_2_confirm'),
              onPressed: () => setState(() => _selfCorrectionStage = 3),
              child: const Text("İlkeyi Onayladım ve Kavradım"),
            ),
          ] else if (_selfCorrectionStage == 3) ...[
            const Text(
              "3. Aşama: Yeniden Temiz Çöz (İzomorfik)",
              key: Key('stage_3_view'),
              style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13),
            ),
            const SizedBox(height: 6),
            const Text(
              "Bu kavram yanılgısını kalıcı olarak gidermek için sentetik ikiz soru çözebilir veya doğrudan temiz çözümü onaylayabilirsin.",
              style: TextStyle(color: Colors.white70, fontSize: 12),
            ),
            const SizedBox(height: 10),
            if (_isGeneratingTwin)
              Container(
                key: const Key('stage_3_generating_twin'),
                padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.black26,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.cyanAccent),
                    ),
                    SizedBox(width: 10),
                    Text(
                      "İzomorfik ikiz soru üretiliyor...",
                      style: TextStyle(color: Colors.cyanAccent, fontSize: 12),
                    ),
                  ],
                ),
              )
            else if (_generatedTwin != null) ...[
              Container(
                key: const Key('stage_3_twin_equation_card'),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.6)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.psychology_outlined, color: Colors.cyanAccent, size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            "İkiz Soru: ${_generatedTwin!.targetEquation}",
                            style: const TextStyle(
                              color: Colors.cyanAccent,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                    if (_generatedTwin!.pedagogicalFocus.isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(
                        "Odak: ${_generatedTwin!.pedagogicalFocus}",
                        style: const TextStyle(color: Colors.white70, fontSize: 11),
                      ),
                    ],
                    if (_generatedTwin!.hint.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        "İpucu: ${_generatedTwin!.hint}",
                        style: const TextStyle(color: Colors.amberAccent, fontSize: 11),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 10),
              if (widget.onLaunchTwinPractice != null) ...[
                ElevatedButton.icon(
                  key: const Key('btn_stage_3_start_practice'),
                  icon: const Icon(Icons.play_arrow_rounded, size: 18),
                  label: const Text("Tuvalde Alıştırmayı Çöz", style: TextStyle(fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.cyanAccent,
                    foregroundColor: Colors.black,
                  ),
                  onPressed: () async {
                    await widget.onLaunchTwinPractice!(item, _generatedTwin!.targetEquation);
                  },
                ),
                const SizedBox(height: 8),
              ],
            ],
            const SizedBox(height: 8),
            Wrap(
              spacing: 8.0,
              runSpacing: 8.0,
              children: [
                OutlinedButton.icon(
                  key: const Key('btn_stage_3_launch_twin'),
                  icon: const Icon(Icons.autorenew, size: 16),
                  label: Text(_generatedTwin != null ? "Yeniden İkiz Üret" : "🎯 İkiz Soru Üret"),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.cyanAccent,
                    side: const BorderSide(color: Colors.cyanAccent),
                  ),
                  onPressed: _isGeneratingTwin
                      ? null
                      : () async {
                          setState(() => _isGeneratingTwin = true);
                          try {
                            final api = widget.apiService ?? EngineApiService();
                            final twin = await api.generateTwinQuestion(
                              bugId: item.bugId,
                              originalEquation: item.problem,
                            );
                            if (mounted) {
                              setState(() {
                                _isGeneratingTwin = false;
                                _generatedTwin = twin;
                              });
                            }
                          } catch (_) {
                            if (mounted) {
                              setState(() => _isGeneratingTwin = false);
                            }
                          }
                        },
                ),
                ElevatedButton.icon(
                  key: const Key('btn_stage_3_complete'),
                  icon: const Icon(Icons.check_circle_outline, size: 16),
                  label: const Text("Temiz Çözümü Tamamla", style: TextStyle(fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.greenAccent,
                    foregroundColor: Colors.black,
                  ),
                  onPressed: () {
                    if (widget.onSelfCorrectionCompleted != null) {
                      widget.onSelfCorrectionCompleted!(item);
                    } else {
                      MistakeVaultService.instance.updateMistakeStatus(item.id, 'cured');
                    }
                    _resetSelfCorrection();
                  },
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
