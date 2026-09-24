import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../ui/core/app_theme.dart';
import '../../../../data/services/engine_api_service.dart';
import '../../../../domain/models/misconception_profile_model.dart';
import '../../session/view_models/session_view_model.dart';

class MisconceptionProfilerScreen extends StatefulWidget {
  final String userId;
  final EngineApiService? apiService;
  final MisconceptionProfileResponse? initialProfile;

  const MisconceptionProfilerScreen({
    super.key,
    this.userId = 'EXP-STU-01',
    this.apiService,
    this.initialProfile,
  });

  @override
  State<MisconceptionProfilerScreen> createState() => _MisconceptionProfilerScreenState();
}

class _MisconceptionProfilerScreenState extends State<MisconceptionProfilerScreen> {
  late final EngineApiService _api;
  MisconceptionProfileResponse? _profile;
  bool _isLoading = true;
  String _selectedCategoryFilter = 'TÜMÜ';

  @override
  void initState() {
    super.initState();
    _api = widget.apiService ?? EngineApiService();
    if (widget.initialProfile != null) {
      _profile = widget.initialProfile;
      _isLoading = false;
    } else {
      _loadProfile();
    }
  }

  Future<void> _loadProfile() async {
    setState(() => _isLoading = true);
    final res = await _api.fetchMisconceptionProfile(widget.userId);
    if (mounted) {
      setState(() {
        _profile = res;
        _isLoading = false;
      });
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'critical':
        return AppColors.accentError; // Rose 500
      case 'warning':
        return AppColors.accentWarning; // Amber 500
      case 'in_remediation':
        return const Color(0xFF38BDF8); // Cyan 400
      case 'mastered':
      case 'cured':
        return AppColors.accentCorrect; // Emerald 500
      default:
        return AppColors.textMuted; // Slate 500
    }
  }

  String _getStatusLabel(String status) {
    switch (status) {
      case 'critical':
        return '🔴 Kritik Zaaf';
      case 'warning':
        return '⚠️ Açık Hata';
      case 'in_remediation':
        return '🔄 Telafide';
      case 'mastered':
      case 'cured':
        return '✅ Aşılmış';
      default:
        return '⚪ Temiz';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        key: const Key('misconception_profiler_app_bar'),
        title: const Text(
          'Kavramsal Yanılgı & Hata Ağacı',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
        ),
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        actions: [
          IconButton(
            key: const Key('refresh_profile_button'),
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            onPressed: _loadProfile,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF38BDF8)),
            )
          : RefreshIndicator(
              onRefresh: _loadProfile,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildOverviewHeader(),
                    const SizedBox(height: 20),
                    _buildTopTrapsSection(),
                    const SizedBox(height: 24),
                    _buildCategoryFilterBar(),
                    const SizedBox(height: 16),
                    _buildConceptTreeMap(),
                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildOverviewHeader() {
    final profile = _profile;
    final total = profile?.totalRecordedMistakes ?? 0;
    final cured = profile?.totalCured ?? 0;
    final rate = profile != null ? (profile.overallCureRate * 100).toStringAsFixed(1) : '0.0';

    return Container(
      key: const Key('misconception_overview_card'),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: const Color(0xFF0284C7).withValues(alpha: 0.2),
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF38BDF8)),
                ),
                child: const Center(
                  child: Text("🧠", style: TextStyle(fontSize: 20)),
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Kişisel Bilişsel Teşhis Profili",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      "Seanslarda yapılan gerçek hataların pedagojik analizi",
                      style: TextStyle(color: AppColors.textSecondary, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildStatChip("Toplam Yanılgı", "$total", Icons.bug_report_outlined, AppColors.accentWarning),
              const SizedBox(width: 10),
              _buildStatChip("Kür Edilen", "$cured", Icons.check_circle_outline, AppColors.accentCorrect),
              const SizedBox(width: 10),
              _buildStatChip("Kür Oranı", "%$rate", Icons.auto_graph, const Color(0xFF38BDF8)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatChip(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: const Color(0xFF0F172A),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(color: color, fontSize: 15, fontWeight: FontWeight.bold),
            ),
            Text(
              label,
              style: const TextStyle(color: AppColors.textSecondary, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeatMapSection([List<MisconceptionCategory>? targetCategories]) {
    final categories = targetCategories ?? _profile?.categories ?? [];
    final allNodes = categories.expand((c) => c.nodes).toList();
    if (allNodes.isEmpty) {
      return const SizedBox.shrink();
    }

    final criticalCount = allNodes.where((n) => n.status == 'critical').length;
    final warningCount = allNodes.where((n) => n.status == 'warning').length;
    final remediationCount = allNodes.where((n) => n.status == 'in_remediation').length;
    final curedCount = allNodes.where((n) => n.status == 'cured' || n.status == 'mastered').length;

    return Container(
      key: const Key('misconception_heat_map_section'),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Text("🔥", style: TextStyle(fontSize: 18)),
                  SizedBox(width: 8),
                  Text(
                    "Kavramsal Isı Haritası",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.accentCorrect.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.accentCorrect.withValues(alpha: 0.4)),
                ),
                child: Text(
                  "$curedCount / ${allNodes.length} Aşılmış",
                  style: const TextStyle(
                    color: AppColors.accentCorrect,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            "Yanılgıların zümrüt yeşiline dönüşümünü takip et",
            style: TextStyle(color: AppColors.textSecondary, fontSize: 12),
          ),
          const SizedBox(height: 14),
          // Legend
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildHeatLegendItem("Kritik", criticalCount, AppColors.accentError),
              _buildHeatLegendItem("Açık Hata", warningCount, AppColors.accentWarning),
              _buildHeatLegendItem("Telafide", remediationCount, const Color(0xFF38BDF8)),
              _buildHeatLegendItem("Aşılmış", curedCount, AppColors.accentCorrect),
            ],
          ),
          const SizedBox(height: 14),
          // Heatmap grid tiles
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: allNodes.map((node) {
              final color = _getStatusColor(node.status);
              return Tooltip(
                message: "${node.title} (${_getStatusLabel(node.status)})",
                child: InkWell(
                  key: Key('heat_tile_${node.bugId}'),
                  borderRadius: BorderRadius.circular(8),
                  onTap: () => _showMisconceptionAutopsySheet(context, node),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.18),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: color, width: 1.2),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: color,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          node.bugId,
                          style: TextStyle(
                            color: color,
                            fontFamily: 'monospace',
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildHeatLegendItem(String label, int count, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          "$label ($count)",
          style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }

  Widget _buildTopTrapsSection() {
    final traps = _profile?.topRecurringTraps ?? [];

    return Column(
      key: const Key('top_traps_section'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Text("🚨", style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Text(
              "En Sık Düşülen 3 Tuzak",
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        if (traps.isEmpty)
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.bgSurface.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white10),
            ),
            child: const Row(
              children: [
                Icon(Icons.sentiment_satisfied_alt, color: AppColors.accentCorrect, size: 20),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    "Harika! Henüz tekrarlayan bir kavramsal tuzak saptanmadı. Çözümlerin temiz.",
                    style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
                  ),
                ),
              ],
            ),
          )
        else
          Column(
            children: traps.map((trap) => _buildTrapCard(trap)).toList(),
          ),
      ],
    );
  }

  Widget _buildTrapCard(MisconceptionNode trap) {
    final color = _getStatusColor(trap.status);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          key: Key('trap_card_${trap.bugId}'),
          onTap: () => _showMisconceptionAutopsySheet(context, trap),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.15),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(Icons.warning_amber_rounded, color: color, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              trap.title,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: color.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              _getStatusLabel(trap.status),
                              style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        trap.cognitiveCause,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Text(
                            "${trap.frequency} kez yapıldı",
                            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                          ),
                          const SizedBox(width: 8),
                          const Text("•", style: TextStyle(color: Color(0xFF64748B))),
                          const SizedBox(width: 8),
                          Text(
                            "FSRS: ${trap.avgStabilityDays.toStringAsFixed(1)} gün",
                            style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 11),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: Colors.white38, size: 18),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCategoryFilterBar() {
    final categories = _profile?.categories ?? [];
    final filterOptions = ['TÜMÜ', ...categories.map((c) => c.categoryTitle)];

    return SizedBox(
      height: 36,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: filterOptions.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final opt = filterOptions[index];
          final isSelected = _selectedCategoryFilter == opt;
          return ChoiceChip(
            label: Text(opt, style: TextStyle(fontSize: 12, color: isSelected ? Colors.white : AppColors.textSecondary)),
            selected: isSelected,
            selectedColor: const Color(0xFF0284C7),
            backgroundColor: AppColors.bgSurface,
            side: BorderSide(color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155)),
            onSelected: (selected) {
              if (selected) {
                setState(() => _selectedCategoryFilter = opt);
              }
            },
          );
        },
      ),
    );
  }

  Widget _buildConceptTreeMap() {
    final categories = _profile?.categories ?? [];
    final filteredCategories = _selectedCategoryFilter == 'TÜMÜ'
        ? categories
        : categories.where((c) => c.categoryTitle == _selectedCategoryFilter).toList();

    return Column(
      key: const Key('concept_tree_section'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Text("🌳", style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Text(
              "Görselleştirilmiş Hata Ağacı (Concept Map)",
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        _buildHeatMapSection(filteredCategories),
        const SizedBox(height: 14),
        ...filteredCategories.map((cat) => _buildCategoryTreeBranch(cat)),
      ],
    );
  }

  Widget _buildCategoryTreeBranch(MisconceptionCategory category) {
    final hasNodes = category.nodes.isNotEmpty;

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: category.activeMistakes > 0 ? AppColors.accentWarning.withValues(alpha: 0.3) : const Color(0xFF334155),
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: ExpansionTile(
          key: Key('category_tile_${category.categoryId}'),
          initiallyExpanded: true,
          leading: Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: (category.activeMistakes > 0 ? AppColors.accentWarning : AppColors.accentCorrect).withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Icon(
                category.activeMistakes > 0 ? Icons.folder_open : Icons.folder_copy_outlined,
                size: 16,
                color: category.activeMistakes > 0 ? AppColors.accentWarning : AppColors.accentCorrect,
              ),
            ),
          ),
          title: Text(
            category.categoryTitle,
            style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
          ),
          subtitle: Text(
            hasNodes
                ? "${category.totalMistakes} Yanılgı (${category.activeMistakes} Aktif, ${category.curedMistakes} Aşılmış)"
                : "Henüz Yanılgı Saptanmadı (Temiz Dal)",
            style: TextStyle(
              color: hasNodes && category.activeMistakes > 0 ? AppColors.accentWarning : AppColors.textSecondary,
              fontSize: 11,
            ),
          ),
          children: hasNodes
              ? category.nodes.map((node) => _buildTreeNodeItem(node)).toList()
              : [
                  const Padding(
                    padding: EdgeInsets.fromLTRB(16, 4, 16, 14),
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        "Bu kategoride kayıtlı kavramsal yanılgı bulunmuyor.",
                        style: TextStyle(color: AppColors.textMuted, fontSize: 12, fontStyle: FontStyle.italic),
                      ),
                    ),
                  ),
                ],
        ),
      ),
    );
  }

  Widget _buildTreeNodeItem(MisconceptionNode node) {
    final color = _getStatusColor(node.status);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          key: Key('node_card_${node.bugId}'),
          borderRadius: BorderRadius.circular(10),
          onTap: () => _showMisconceptionAutopsySheet(context, node),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              node.title,
                              style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                            ),
                          ),
                          Text(
                            node.bugId,
                            style: TextStyle(color: color, fontSize: 10, fontFamily: 'monospace'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        node.cognitiveCause,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: AppColors.textSecondary, fontSize: 11),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    _getStatusLabel(node.status),
                    style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showMisconceptionAutopsySheet(BuildContext context, MisconceptionNode node) {
    final color = _getStatusColor(node.status);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Container(
        key: const Key('misconception_detail_sheet'),
        padding: const EdgeInsets.all(20),
        decoration: const BoxDecoration(
          color: Color(0xFF0F172A),
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          border: Border(top: BorderSide(color: Color(0xFF38BDF8), width: 2)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        node.title,
                        style: const TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        "${node.categoryTitle} • ${node.bugId}",
                        style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.white70),
                  onPressed: () => Navigator.of(ctx).pop(),
                ),
              ],
            ),
            const Divider(color: Color(0xFF1E293B), height: 24),

            // Bilişsel Sebep
            const Text(
              "🔍 Bilişsel Sebep (Neden Bu Hataya Düşülüyor?):",
              style: TextStyle(color: AppColors.accentWarning, fontSize: 12, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              node.cognitiveCause,
              style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4),
            ),
            const SizedBox(height: 14),

            // Son Hatalı Adım
            if (node.lastOffendingStep != null) ...[
              const Text(
                "❌ Seansındaki Son Hatalı Adımın:",
                style: TextStyle(color: AppColors.accentError, fontSize: 12, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.accentError.withValues(alpha: 0.3)),
                ),
                child: Text(
                  MathTypography.toPrettyMath(node.lastOffendingStep!),
                  style: const TextStyle(color: Colors.white, fontFamily: 'monospace', fontSize: 14),
                ),
              ),
              const SizedBox(height: 14),
            ],

            // Doğru İlke
            const Text(
              "✅ Doğru Matematiksel İlke:",
              style: TextStyle(color: AppColors.accentCorrect, fontSize: 12, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.accentCorrect.withValues(alpha: 0.3)),
              ),
              child: Text(
                node.correctPrinciple.isNotEmpty ? node.correctPrinciple : node.remediationDirective,
                style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4),
              ),
            ),
            const SizedBox(height: 14),

            // Sokratik Yönlendirme
            if (node.remediationDirective.isNotEmpty) ...[
              const Text(
                "💡 Sokratik Reçete:",
                style: TextStyle(color: Color(0xFF38BDF8), fontSize: 12, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                node.remediationDirective,
                style: const TextStyle(color: AppColors.textSecondary, fontSize: 12, fontStyle: FontStyle.italic),
              ),
              const SizedBox(height: 20),
            ],

            // Twin Practice CTA Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                key: const Key('start_twin_practice_button'),
                icon: const Icon(Icons.track_changes, size: 18),
                label: const Text("🎯 İkiz Soru Üret & Alıştırmaya Başla"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0284C7),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () async {
                  Navigator.of(ctx).pop();
                  final messenger = ScaffoldMessenger.of(context);
                  messenger.showSnackBar(
                    SnackBar(
                      content: Text("${node.title} için ikiz soru üretiliyor..."),
                      backgroundColor: const Color(0xFF0284C7),
                      duration: const Duration(seconds: 1),
                    ),
                  );
                  final twin = await _api.generateTwinQuestion(bugId: node.bugId);
                  if (context.mounted) {
                    try {
                      final vm = context.read<SessionViewModel>();
                      vm.startNewTarget(
                        newTargetEquation: twin.targetEquation,
                        newNodeId: 'TWIN-${node.bugId}',
                      );
                      Navigator.of(context).pop();
                    } catch (_) {
                      if (context.mounted) {
                        messenger.hideCurrentSnackBar();
                        messenger.showSnackBar(
                          SnackBar(
                            content: Text("İkiz soru hazırlandı: ${twin.targetEquation}"),
                            backgroundColor: const Color(0xFF0284C7),
                          ),
                        );
                      }
                    }
                  }
                },
              ),
            ),
            const SizedBox(height: 8),

            // CTA Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                key: const Key('start_remediation_cta_button'),
                icon: const Icon(Icons.healing_outlined, size: 18),
                label: const Text("Bu Yanılgıyı Kendi Kendine Telafi Et"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.accentPrimary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                onPressed: () {
                  Navigator.of(ctx).pop();
                  // Open MistakeAutopsyView or self-correction
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text("${node.title} için telafi seansı hazırlanıyor..."),
                      backgroundColor: AppColors.accentPrimary,
                      duration: const Duration(seconds: 2),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 10),
          ],
        ),
      ),
    );
  }
}
