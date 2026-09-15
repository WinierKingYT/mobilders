import 'package:flutter/material.dart';
import '../../../../ui/core/app_theme.dart';

class AtlasNodeModel {
  final String id;
  final String title;
  final String domain;
  final int level;
  final String status; // 'MASTERED', 'IN_ZPD', 'LOCKED'
  final List<String> prerequisites;
  final String description;

  const AtlasNodeModel({
    required this.id,
    required this.title,
    required this.domain,
    required this.level,
    required this.status,
    required this.prerequisites,
    required this.description,
  });
}

class LivingKnowledgeAtlasView extends StatefulWidget {
  final List<AtlasNodeModel>? nodes;

  const LivingKnowledgeAtlasView({
    super.key,
    this.nodes,
  });

  @override
  State<LivingKnowledgeAtlasView> createState() => _LivingKnowledgeAtlasViewState();
}

class _LivingKnowledgeAtlasViewState extends State<LivingKnowledgeAtlasView> {
  late List<AtlasNodeModel> _allNodes;
  String _selectedDomain = 'Tümü';
  String _searchQuery = '';
  AtlasNodeModel? _inspectedNode;

  final List<String> _domains = [
    'Tümü',
    'Temel Kökler & Sezgi',
    'Cebir & Polinomlar',
    'Trigonometri & Fonksiyonlar',
    'Diferansiyel Analiz (Türev)',
    'İntegral Analizi',
    'Analitik Geometri & Vektörler',
    'Sentetik Öklid Geometrisi',
    'Kombinatorik & Olasılık',
    'Mantık & Matematiksel İspat',
  ];

  @override
  void initState() {
    super.initState();
    _allNodes = widget.nodes ?? _generateSampleNodes();
  }

  List<AtlasNodeModel> get _filteredNodes {
    return _allNodes.where((node) {
      final matchesDomain = _selectedDomain == 'Tümü' || node.domain == _selectedDomain;
      final matchesSearch = _searchQuery.isEmpty ||
          node.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          node.id.toLowerCase().contains(_searchQuery.toLowerCase());
      return matchesDomain && matchesSearch;
    }).toList();
  }

  int get _masteredCount => _allNodes.where((n) => n.status == 'MASTERED').length;
  int get _zpdCount => _allNodes.where((n) => n.status == 'IN_ZPD').length;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Stats Overview Bar
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          color: Colors.black38,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem('Toplam Düğüm', '${_allNodes.length}', Colors.white),
              _buildStatItem('Usta Olunan', '$_masteredCount', AppColors.accentCorrect),
              _buildStatItem('ZPD (Hazır)', '$_zpdCount', Colors.blueAccent),
            ],
          ),
        ),

        // Search Bar
        Padding(
          padding: const EdgeInsets.fromLTRB(16.0, 12.0, 16.0, 6.0),
          child: TextField(
            key: const Key('atlas_search_field'),
            decoration: InputDecoration(
              hintText: 'Düğüm veya kavram ara (örn: Türev, Polinom, N01)...',
              hintStyle: const TextStyle(color: Colors.white54, fontSize: 13.0),
              prefixIcon: const Icon(Icons.search, color: Colors.white70),
              filled: true,
              fillColor: Colors.white10,
              contentPadding: const EdgeInsets.symmetric(vertical: 10.0),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12.0),
                borderSide: BorderSide.none,
              ),
            ),
            style: const TextStyle(color: Colors.white),
            onChanged: (val) => setState(() => _searchQuery = val),
          ),
        ),

        // Domain Filter Chips
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
          child: Row(
            children: _domains.map((domain) {
              final isSelected = _selectedDomain == domain;
              return Padding(
                padding: const EdgeInsets.only(right: 8.0),
                child: FilterChip(
                  key: Key('chip_domain_$domain'),
                  label: Text(domain),
                  selected: isSelected,
                  selectedColor: AppColors.accentCorrect.withValues(alpha: 0.25),
                  checkmarkColor: AppColors.accentCorrect,
                  labelStyle: TextStyle(
                    color: isSelected ? AppColors.accentCorrect : Colors.white70,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    fontSize: 12.0,
                  ),
                  onSelected: (val) {
                    setState(() {
                      _selectedDomain = val ? domain : 'Tümü';
                    });
                  },
                ),
              );
            }).toList(),
          ),
        ),

        // Nodes List
        Expanded(
          child: _filteredNodes.isEmpty
              ? const Center(
                  child: Text(
                    'Aranan kriterlere uygun düğüm bulunamadı.',
                    style: TextStyle(color: Colors.white54),
                  ),
                )
              : ListView.builder(
                  key: const Key('atlas_nodes_list'),
                  padding: const EdgeInsets.all(12.0),
                  itemCount: _filteredNodes.length,
                  itemBuilder: (context, index) {
                    final node = _filteredNodes[index];
                    return _buildNodeCard(node);
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(value, style: TextStyle(color: color, fontSize: 18.0, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2.0),
        Text(label, style: const TextStyle(color: Colors.white60, fontSize: 11.0)),
      ],
    );
  }

  Widget _buildNodeCard(AtlasNodeModel node) {
    Color statusColor;
    String statusText;
    switch (node.status) {
      case 'MASTERED':
        statusColor = AppColors.accentCorrect;
        statusText = 'USTA';
        break;
      case 'IN_ZPD':
        statusColor = Colors.blueAccent;
        statusText = 'ZPD (HAZIR)';
        break;
      default:
        statusColor = Colors.grey;
        statusText = 'KİLİTLİ';
    }

    return Card(
      key: Key('node_card_${node.id}'),
      color: Colors.white.withValues(alpha: 0.06),
      margin: const EdgeInsets.symmetric(vertical: 4.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10.0),
        side: BorderSide(
          color: node.status == 'IN_ZPD' ? Colors.blueAccent.withValues(alpha: 0.5) : Colors.transparent,
          width: 1.2,
        ),
      ),
      child: ListTile(
        onTap: () => _showNodeDetailSheet(node),
        leading: CircleAvatar(
          backgroundColor: statusColor.withValues(alpha: 0.2),
          child: Text(
            node.id.replaceFirst('N_ROOT_', 'R').replaceFirst('N', ''),
            style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 11.0),
          ),
        ),
        title: Text(
          node.title,
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14.0),
        ),
        subtitle: Text(
          '${node.domain} • Seviye ${node.level}',
          style: const TextStyle(color: Colors.white54, fontSize: 12.0),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
          decoration: BoxDecoration(
            color: statusColor.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(6.0),
          ),
          child: Text(
            statusText,
            style: TextStyle(color: statusColor, fontSize: 11.0, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  void _showNodeDetailSheet(AtlasNodeModel node) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.bgPrimary,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20.0)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    node.id,
                    style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 16.0),
                  ),
                  Text(
                    node.domain,
                    style: const TextStyle(color: Colors.white54, fontSize: 12.0),
                  ),
                ],
              ),
              const SizedBox(height: 8.0),
              Text(
                node.title,
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18.0),
              ),
              const SizedBox(height: 8.0),
              Text(
                node.description,
                style: const TextStyle(color: Colors.white70, fontSize: 13.0),
              ),
              const SizedBox(height: 12.0),
              if (node.prerequisites.isNotEmpty) ...[
                const Text('Önkoşullar:', style: TextStyle(color: Colors.white70, fontWeight: FontWeight.bold, fontSize: 12.0)),
                const SizedBox(height: 4.0),
                Wrap(
                  spacing: 6.0,
                  children: node.prerequisites.map((p) => Chip(
                    backgroundColor: Colors.white10,
                    label: Text(p, style: const TextStyle(color: Colors.white70, fontSize: 11.0)),
                  )).toList(),
                ),
              ],
              const SizedBox(height: 16.0),
              ElevatedButton.icon(
                key: const Key('btn_start_learning_path'),
                icon: const Icon(Icons.school),
                label: const Text('Öğrenme Yolunu Başlat'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.accentCorrect,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 12.0),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
                ),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
        );
      },
    );
  }

  static List<AtlasNodeModel> _generateSampleNodes() {
    return [
      const AtlasNodeModel(
        id: 'N_ROOT_01',
        title: 'Sayı Doğrusu ve Yön Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: -3,
        status: 'MASTERED',
        prerequisites: [],
        description: 'Sıfırın sağı kazanç, solu kayıptır; sola gidildikçe değer küçülür.',
      ),
      const AtlasNodeModel(
        id: 'N01',
        title: 'Tam Sayılarda Dört İşlem ve İşaret Kuralları',
        domain: 'Cebir & Polinomlar',
        level: 0,
        status: 'MASTERED',
        prerequisites: ['N_ROOT_01'],
        description: 'İşlem önceliği ve işaret çarpım kuralları.',
      ),
      const AtlasNodeModel(
        id: 'N02',
        title: 'İşlem Önceliği ve Parantez Açma',
        domain: 'Cebir & Polinomlar',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: ['N01'],
        description: 'Çarpma/bölme önceliği ve dağılma özelliği.',
      ),
      const AtlasNodeModel(
        id: 'N91',
        title: 'Toplam ve Farkın Türevi',
        domain: 'Diferansiyel Analiz (Türev)',
        level: 11,
        status: 'LOCKED',
        prerequisites: ['N89', 'N90'],
        description: '(f ± g) türevi polinom türev kuralı.',
      ),
      const AtlasNodeModel(
        id: 'N227',
        title: 'Matematiksel Tümevarım: Hipotez ve Geçiş Adımı',
        domain: 'Mantık & Matematiksel İspat',
        level: 19,
        status: 'LOCKED',
        prerequisites: ['N226'],
        description: 'P(k) kabulü ve P(k+1) türetimi.',
      ),
    ];
  }
}
