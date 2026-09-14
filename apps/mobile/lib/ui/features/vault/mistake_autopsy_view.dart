import 'package:flutter/material.dart';

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
}

class MistakeAutopsyView extends StatefulWidget {
  final List<MistakeAutopsyItem> mistakes;
  final VoidCallback? onStartBossBattle;
  final ValueChanged<MistakeAutopsyItem>? onSelfCorrectionCompleted;

  const MistakeAutopsyView({
    super.key,
    required this.mistakes,
    this.onStartBossBattle,
    this.onSelfCorrectionCompleted,
  });

  @override
  State<MistakeAutopsyView> createState() => _MistakeAutopsyViewState();
}

class _MistakeAutopsyViewState extends State<MistakeAutopsyView> {
  MistakeFilter _filter = MistakeFilter.all;
  MistakeAutopsyItem? _activeSelfCorrectionItem;
  int _selfCorrectionStage = 1; // 1: Teşhis, 2: İlke, 3: Temiz Çözüm

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
                if (_filteredMistakes.isEmpty)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32.0),
                      child: Text(
                        "Bu kategoride kayıtlı hata bulunmuyor. Zihnin pırıl pırıl!",
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
                onPressed: () => setState(() => _activeSelfCorrectionItem = null),
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
            const Text("Taze soru hazırlanıyor. Doğru adımı uygulayarak soruyu çöz."),
            const SizedBox(height: 12),
            ElevatedButton(
              key: const Key('btn_stage_3_complete'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent, foregroundColor: Colors.black),
              onPressed: () {
                widget.onSelfCorrectionCompleted?.call(item);
                setState(() => _activeSelfCorrectionItem = null);
              },
              child: const Text("Temiz Çözümü Tamamla", style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ],
        ],
      ),
    );
  }
}
