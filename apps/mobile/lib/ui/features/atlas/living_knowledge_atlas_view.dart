import 'package:flutter/material.dart';
import '../../../../ui/core/app_theme.dart';
import '../../../../data/services/engine_api_service.dart';

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

  factory AtlasNodeModel.fromJson(Map<String, dynamic> json) {
    return AtlasNodeModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      domain: json['domain'] as String? ?? 'Cebir & Polinomlar',
      level: (json['level'] as num?)?.toInt() ?? 0,
      status: json['status'] as String? ?? 'LOCKED',
      prerequisites: (json['prerequisites'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? const [],
      description: json['description'] as String? ?? '',
    );
  }
}

class LivingKnowledgeAtlasView extends StatefulWidget {
  final List<AtlasNodeModel>? nodes;
  final EngineApiService? apiService;

  const LivingKnowledgeAtlasView({
    super.key,
    this.nodes,
    this.apiService,
  });

  @override
  State<LivingKnowledgeAtlasView> createState() => _LivingKnowledgeAtlasViewState();
}

class _LivingKnowledgeAtlasViewState extends State<LivingKnowledgeAtlasView> {
  late List<AtlasNodeModel> _allNodes;
  String _selectedDomain = 'Tümü';
  String _searchQuery = '';
  bool _isCanvasMode = false;

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
    if (widget.nodes != null) {
      _allNodes = widget.nodes!;
    } else {
      _allNodes = _generateInitialRootNodes();
      _loadRealNodes();
    }
  }

  @override
  void didUpdateWidget(covariant LivingKnowledgeAtlasView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.nodes != null && widget.nodes != oldWidget.nodes) {
      _allNodes = widget.nodes!;
    }
  }

  Future<void> _loadRealNodes() async {
    try {
      final service = widget.apiService ?? EngineApiService();
      final payload = await service.fetchAtlasPayload();
      final rawNodes = payload['nodes'] as List<dynamic>?;
      if (rawNodes != null && rawNodes.isNotEmpty && mounted) {
        setState(() {
          _allNodes = rawNodes.map((n) => AtlasNodeModel.fromJson(n as Map<String, dynamic>)).toList();
        });
      }
    } catch (_) {
      // Keep initial honest root nodes if offline
    }
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

        // View Mode Toggle (Liste vs DAG Kanvası)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              SegmentedButton<bool>(
                key: const Key('toggle_atlas_view_mode'),
                segments: const [
                  ButtonSegment<bool>(
                    value: false,
                    icon: Icon(Icons.list_alt, size: 16),
                    label: Text('Liste', style: TextStyle(fontSize: 12)),
                  ),
                  ButtonSegment<bool>(
                    value: true,
                    icon: Icon(Icons.hub_outlined, size: 16),
                    label: Text('DAG Kanvası', style: TextStyle(fontSize: 12)),
                  ),
                ],
                selected: {_isCanvasMode},
                onSelectionChanged: (set) => setState(() => _isCanvasMode = set.first),
                style: SegmentedButton.styleFrom(
                  backgroundColor: Colors.white10,
                  selectedBackgroundColor: AppColors.accentCorrect.withValues(alpha: 0.3),
                  selectedForegroundColor: Colors.white,
                  foregroundColor: Colors.white70,
                ),
              ),
            ],
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

        // Content Area: List or DAG Canvas with RepaintBoundary Isolation
        Expanded(
          child: _filteredNodes.isEmpty
              ? const Center(
                  child: Text(
                    'Aranan kriterlere uygun düğüm bulunamadı.',
                    style: TextStyle(color: Colors.white54),
                  ),
                )
              : (_isCanvasMode
                  ? _buildDagCanvasView()
                  : ListView.builder(
                      key: const Key('atlas_nodes_list'),
                      padding: const EdgeInsets.all(12.0),
                      itemCount: _filteredNodes.length,
                      itemBuilder: (context, index) {
                        final node = _filteredNodes[index];
                        // RepaintBoundary isolates each list item into its own GPU display list
                        return RepaintBoundary(
                          key: Key('repaint_node_${node.id}'),
                          child: _buildNodeCard(node),
                        );
                      },
                    )),
        ),
      ],
    );
  }

  Widget _buildDagCanvasView() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return ClipRect(
          child: InteractiveViewer(
            key: const Key('atlas_dag_interactive_viewer'),
            boundaryMargin: const EdgeInsets.all(300),
            minScale: 0.4,
            maxScale: 2.5,
            child: SizedBox(
              width: 1400,
              height: 1000,
              child: Stack(
                children: [
                  // Layer 1: Static Grid isolated via RepaintBoundary
                  const Positioned.fill(
                    child: RepaintBoundary(
                      key: Key('atlas_grid_repaint_boundary'),
                      child: CustomPaint(
                        painter: KnowledgeDagGridPainter(),
                      ),
                    ),
                  ),
                  // Layer 2: Dynamic DAG Nodes & Prerequisite Edges isolated via RepaintBoundary
                  Positioned.fill(
                    child: RepaintBoundary(
                      key: const Key('atlas_dag_repaint_boundary'),
                      child: CustomPaint(
                        painter: KnowledgeDagPainter(
                          nodes: _filteredNodes,
                          sanitizedZoomScale: 1.0,
                        ),
                      ),
                    ),
                  ),
                  // Layer 3: Interactive Node Tap Targets with NaN-guarded coordinates
                  ..._filteredNodes.map((node) {
                    final pos = KnowledgeDagPainter.calculateNodePosition(
                      node: node,
                      allNodes: _filteredNodes,
                    );
                    return Positioned(
                      left: pos.dx - 24,
                      top: pos.dy - 24,
                      child: GestureDetector(
                        key: Key('dag_node_tap_${node.id}'),
                        onTap: () => _showNodeDetailSheet(node),
                        child: Container(
                          width: 48,
                          height: 48,
                          color: Colors.transparent,
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
        );
      },
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

  static List<AtlasNodeModel> _generateInitialRootNodes() {
    return [
      const AtlasNodeModel(
        id: 'N_ROOT_01',
        title: 'Sayı Doğrusu ve Yön Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Sıfırın sağı kazanç, solu kayıptır; sola gidildikçe değer küçülür.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_02',
        title: 'Eşitlik ve İki Kefeli Terazi Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Denklem terazidir; her iki tarafa aynı işlem uygulanınca denge bozulmaz.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_03',
        title: 'Negatif Sayı ve Borç/Kayıp Metaforu',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Eksi işaretinin borç ve yön değişimi anlamı.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_04',
        title: 'Alan ve Çarpma Geometrisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Çarpma işlemi dikdörtgensel alan modelidir.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_05',
        title: 'Bölme ve Paylaştırma Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Eşit paylaştırma ve ters çarpma mantığı.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_06',
        title: 'Oran, Orantı ve Benzerlik',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Birim dönüşümleri ve benzer üçgen oranları.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_07',
        title: 'Değişken ve Bilinmeyen Kutusu',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'x bir kutudur; içine değerler konulur.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_08',
        title: 'Koordinat Sistemi ve Konum Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: '2B düzlemde (x, y) adresleme ve mesafe.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_09',
        title: 'Eğim ve Diklik Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Yükseklik/uzaklık oranı ve diklik kuralı.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_10',
        title: 'Açı ve Dönme Hareketi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Dairesel yay ve açı kavramı.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_11',
        title: 'Üstel Büyüme ve Katlanma Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Sürekli ikiye katlanma ve geometrik artış.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_12',
        title: 'Logaritma ve Basamak Sayma Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Katlanmanın tersi; kaç kez çarpıldığını bulma.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_13',
        title: 'Limit ve Yaklaşma Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Bir noktaya sonsuz yaklaşma ama asla dokunmama.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_14',
        title: 'Türev ve Anlık Hız Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Kilometre göstergesindeki anlık ibre hızı.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_15',
        title: 'İntegral ve Birikim Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Damlayan suyun kovayı doldurması gibi birikim alanı.',
      ),
      const AtlasNodeModel(
        id: 'N_ROOT_16',
        title: 'Olasılık ve Şans Sezgisi',
        domain: 'Temel Kökler & Sezgi',
        level: 0,
        status: 'IN_ZPD',
        prerequisites: [],
        description: 'Zar atma, yazı-tura ve adil şans dağılımı.',
      ),
    ];
  }
}

/// Static grid painter isolated via RepaintBoundary to eliminate GPU jank
class KnowledgeDagGridPainter extends CustomPainter {
  const KnowledgeDagGridPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withValues(alpha: 0.04)
      ..strokeWidth = 1.0;

    const gridSize = 40.0;
    final w = KnowledgeDagPainter.sanitizeCoordinate(size.width, fallback: 1400);
    final h = KnowledgeDagPainter.sanitizeCoordinate(size.height, fallback: 1000);

    for (double x = 0; x <= w; x += gridSize) {
      canvas.drawLine(Offset(x, 0), Offset(x, h), paint);
    }
    for (double y = 0; y <= h; y += gridSize) {
      canvas.drawLine(Offset(0, y), Offset(w, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Dynamic DAG node and prerequisite graph painter isolated via RepaintBoundary
class KnowledgeDagPainter extends CustomPainter {
  final List<AtlasNodeModel> nodes;
  final double sanitizedZoomScale;

  KnowledgeDagPainter({
    required this.nodes,
    double sanitizedZoomScale = 1.0,
  }) : sanitizedZoomScale = sanitizeCoordinate(sanitizedZoomScale, fallback: 1.0);

  /// Strict NaN and Infinity guard protecting rendering engine during rapid pinch-zooms
  static double sanitizeCoordinate(double val, {double fallback = 0.0}) {
    if (val.isNaN || val.isInfinite) return fallback;
    return val;
  }

  static Offset sanitizeOffset(Offset offset, {Offset fallback = Offset.zero}) {
    if (offset.dx.isNaN || offset.dx.isInfinite || offset.dy.isNaN || offset.dy.isInfinite) {
      return fallback;
    }
    return offset;
  }

  static Offset calculateNodePosition({
    required AtlasNodeModel node,
    required List<AtlasNodeModel> allNodes,
  }) {
    final sameLevelNodes = allNodes.where((n) => n.level == node.level).toList();
    final indexInLevel = sameLevelNodes.indexOf(node);
    final safeIndex = indexInLevel >= 0 ? indexInLevel : 0;

    final x = sanitizeCoordinate(120.0 + (node.level * 220.0), fallback: 120.0);
    final y = sanitizeCoordinate(90.0 + (safeIndex * 110.0), fallback: 90.0);
    return Offset(x, y);
  }

  @override
  void paint(Canvas canvas, Size size) {
    if (nodes.isEmpty) return;

    final edgePaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.22)
      ..strokeWidth = 1.8
      ..style = PaintingStyle.stroke;

    final nodePosMap = <String, Offset>{};
    for (final node in nodes) {
      nodePosMap[node.id] = calculateNodePosition(node: node, allNodes: nodes);
    }

    // Draw DAG prerequisite curves
    for (final node in nodes) {
      final childPos = nodePosMap[node.id];
      if (childPos == null) continue;

      for (final prereqId in node.prerequisites) {
        final parentPos = nodePosMap[prereqId];
        if (parentPos != null) {
          final p1 = sanitizeOffset(parentPos);
          final p2 = sanitizeOffset(childPos);

          final path = Path()
            ..moveTo(p1.dx, p1.dy)
            ..cubicTo(
              sanitizeCoordinate(p1.dx + 80),
              p1.dy,
              sanitizeCoordinate(p2.dx - 80),
              p2.dy,
              p2.dx,
              p2.dy,
            );
          canvas.drawPath(path, edgePaint);
        }
      }
    }

    // Draw DAG Nodes with status colors
    for (final node in nodes) {
      final pos = nodePosMap[node.id];
      if (pos == null) continue;
      final safePos = sanitizeOffset(pos);

      Color statusColor;
      switch (node.status) {
        case 'MASTERED':
          statusColor = AppColors.accentCorrect;
          break;
        case 'IN_ZPD':
          statusColor = Colors.blueAccent;
          break;
        default:
          statusColor = Colors.grey;
      }

      // Outer glow / halo
      final bgPaint = Paint()
        ..color = statusColor.withValues(alpha: 0.25)
        ..style = PaintingStyle.fill;
      canvas.drawCircle(safePos, 22.0, bgPaint);

      // Node border
      final circlePaint = Paint()
        ..color = statusColor
        ..strokeWidth = 2.0
        ..style = PaintingStyle.stroke;
      canvas.drawCircle(safePos, 20.0, circlePaint);

      // Node ID text
      final textPainter = TextPainter(
        text: TextSpan(
          text: node.id.replaceFirst('N_ROOT_', 'R').replaceFirst('N', ''),
          style: const TextStyle(
            color: Colors.white,
            fontSize: 11.0,
            fontWeight: FontWeight.bold,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();

      textPainter.paint(
        canvas,
        Offset(
          sanitizeCoordinate(safePos.dx - (textPainter.width / 2)),
          sanitizeCoordinate(safePos.dy - (textPainter.height / 2)),
        ),
      );
    }
  }

  @override
  bool shouldRepaint(covariant KnowledgeDagPainter oldDelegate) {
    return oldDelegate.nodes != nodes || oldDelegate.sanitizedZoomScale != sanitizedZoomScale;
  }
}
