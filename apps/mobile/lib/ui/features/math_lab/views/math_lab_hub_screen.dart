import 'package:flutter/material.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../session/views/al_khwarizmi_canvas.dart';
import '../../session/views/unit_circle_canvas.dart';
import '../../session/views/dynamic_tangent_canvas.dart';
import '../../session/views/riemann_integral_canvas.dart';
import '../../session/views/interactive_coordinate_canvas.dart';
import '../../session/views/euclidean_canvas.dart';
import '../../session/views/counting_tree_venn_canvas.dart';
import '../../root_pedagogy/number_line_balance_canvas.dart';
import '../../modeling/problem_modeling_view.dart';
import '../../scanner/math_scanner_view.dart';

class MathLabItem {
  final String id;
  final String title;
  final String category;
  final String description;
  final IconData icon;
  final Color accentColor;
  final Widget Function(BuildContext) builder;

  const MathLabItem({
    required this.id,
    required this.title,
    required this.category,
    required this.description,
    required this.icon,
    required this.accentColor,
    required this.builder,
  });
}

class MathLabHubScreen extends StatefulWidget {
  const MathLabHubScreen({super.key});

  @override
  State<MathLabHubScreen> createState() => _MathLabHubScreenState();
}

class _MathLabHubScreenState extends State<MathLabHubScreen> {
  String _selectedCategory = 'Tümü';
  String _searchQuery = '';

  final List<String> _categories = [
    'Tümü',
    'Cebir',
    'Trigonometri',
    'Kalkülüs',
    'Geometri',
    'Modelleme & AI',
  ];

  late final List<MathLabItem> _labItems = [
    MathLabItem(
      id: 'al_khwarizmi',
      title: 'El-Harezmi Cebir Karoları',
      category: 'Cebir',
      description: 'Kare tamamlama ve iki kare farkını geometrik alanlarla somutlaştırın.',
      icon: Icons.architecture,
      accentColor: const Color(0xFF10B981),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: AlKhwarizmiCanvas(bCoefficient: 6.0)),
      ),
    ),
    MathLabItem(
      id: 'unit_circle',
      title: 'Birim Çember & Trigonometri',
      category: 'Trigonometri',
      description: 'Dinamik açı manipülasyonu ile sin, cos, tan izdüşümlerini interaktif keşfedin.',
      icon: Icons.change_circle_outlined,
      accentColor: const Color(0xFFF59E0B),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: UnitCircleCanvas()),
      ),
    ),
    MathLabItem(
      id: 'dynamic_tangent',
      title: 'Dinamik Teğet & Türev Eğimi',
      category: 'Kalkülüs',
      description: 'Fonksiyon üzerindeki anlık değişim oranını ve teğet doğrusunu dinamik izleyin.',
      icon: Icons.show_chart_rounded,
      accentColor: const Color(0xFF38BDF8),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: DynamicTangentCanvas()),
      ),
    ),
    MathLabItem(
      id: 'riemann_integral',
      title: 'Riemann İntegrali & Alan',
      category: 'Kalkülüs',
      description: 'Sol, sağ, orta nokta ve yamuk integrasyon yöntemleriyle eğri altındaki alanı hesaplayın.',
      icon: Icons.area_chart_rounded,
      accentColor: const Color(0xFF34D399),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: RiemannIntegralCanvas()),
      ),
    ),
    MathLabItem(
      id: 'coordinate_vector',
      title: 'Analitik Koordinat & Vektör',
      category: 'Geometri',
      description: '2B koordinat düzleminde vektör toplama, nokta öteleme ve eğim analizleri yapın.',
      icon: Icons.grid_4x4_rounded,
      accentColor: const Color(0xFF6366F1),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: InteractiveCoordinateCanvas()),
      ),
    ),
    MathLabItem(
      id: 'euclidean_canvas',
      title: 'Sentetik Öklid & Ek Çizim',
      category: 'Geometri',
      description: 'Açıortay, kenarortay ve yardımcı çizgi stratejileriyle sentetik geometrik ispatlar kurun.',
      icon: Icons.architecture_rounded,
      accentColor: const Color(0xFFF43F5E),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: EuclideanCanvas()),
      ),
    ),
    MathLabItem(
      id: 'counting_tree_venn',
      title: 'Sayma Ağacı & Venn Şeması',
      category: 'Cebir',
      description: 'Kombinatorik sayma kuralları, permütasyon ve küme kesişimlerini görselleştirin.',
      icon: Icons.account_tree_rounded,
      accentColor: const Color(0xFFA855F7),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: CountingTreeVennCanvas()),
      ),
    ),
    MathLabItem(
      id: 'number_line_balance',
      title: 'Sayı Doğrusu & Denklem Dengesi',
      category: 'Cebir',
      description: 'Negatif sayılar ve cebirsel denklik prensiplerini terazi modeliyle inceleyin.',
      icon: Icons.balance_rounded,
      accentColor: const Color(0xFF14B8A6),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: NumberLineBalanceCanvas()),
      ),
    ),
    MathLabItem(
      id: 'problem_modeling',
      title: 'Problem Modelleme İskelesi',
      category: 'Modelleme & AI',
      description: 'Yeni nesil hikayeli soruları hareket diyagramları ve karışım kaplarıyla modelleyin.',
      icon: Icons.auto_stories_outlined,
      accentColor: const Color(0xFFF59E0B),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: ProblemModelingView()),
      ),
    ),
    MathLabItem(
      id: 'math_scanner',
      title: 'Sokratik Defter & Soru Kamerası',
      category: 'Modelleme & AI',
      description: 'El yazısı matematik adımlarınızı ve soru fotoğraflarını yapay zeka ile analiz edin.',
      icon: Icons.camera_alt_outlined,
      accentColor: const Color(0xFF38BDF8),
      builder: (_) => const Scaffold(
        backgroundColor: Color(0xFF090D16),
        body: SafeArea(child: MathScannerView()),
      ),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final filteredItems = _labItems.where((item) {
      final matchesCategory = _selectedCategory == 'Tümü' || item.category == _selectedCategory;
      final matchesQuery = _searchQuery.isEmpty ||
          item.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          item.description.toLowerCase().contains(_searchQuery.toLowerCase());
      return matchesCategory && matchesQuery;
    }).toList();

    return Scaffold(
      key: const Key('math_lab_hub_screen'),
      backgroundColor: const Color(0xFF090D16),
      appBar: AppBar(
        title: const Text(
          'Matematik Laboratuvarı',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Search Bar & Filter Header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            color: const Color(0xFF0F172A),
            child: Column(
              children: [
                TextField(
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Kanvas veya model ara (örn: Türev, Öklid)...',
                    hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 14),
                    prefixIcon: const Icon(Icons.search, color: Color(0xFF64748B), size: 20),
                    filled: true,
                    fillColor: const Color(0xFF1E293B),
                    contentPadding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onChanged: (val) => setState(() => _searchQuery = val),
                ),
                const SizedBox(height: 10),
                // Category Chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: _categories.map((cat) {
                      final isSelected = _selectedCategory == cat;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(cat),
                          selected: isSelected,
                          selectedColor: const Color(0xFF38BDF8),
                          backgroundColor: const Color(0xFF1E293B),
                          labelStyle: TextStyle(
                            color: isSelected ? const Color(0xFF090D16) : const Color(0xFF94A3B8),
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                            fontSize: 12,
                          ),
                          onSelected: (selected) {
                            if (selected) {
                              HapticFeedbackService().selectionClick();
                              setState(() => _selectedCategory = cat);
                            }
                          },
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),

          // Lab Items Grid / List
          Expanded(
            child: filteredItems.isEmpty
                ? const Center(
                    child: Text(
                      'Aramanıza uygun matematik kanvası bulunamadı.',
                      style: TextStyle(color: Color(0xFF94A3B8)),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: filteredItems.length,
                    itemBuilder: (context, index) {
                      final item = filteredItems[index];
                      return _buildLabCard(context, item);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildLabCard(BuildContext context, MathLabItem item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () {
            HapticFeedbackService().selectionClick();
            Navigator.of(context).push(
              MaterialPageRoute(builder: item.builder),
            );
          },
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: item.accentColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: item.accentColor.withValues(alpha: 0.3)),
                  ),
                  child: Icon(item.icon, color: item.accentColor, size: 28),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              item.title,
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 15,
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0F172A),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              item.category,
                              style: TextStyle(
                                color: item.accentColor,
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        item.description,
                        style: const TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 13,
                          height: 1.3,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                const Icon(Icons.arrow_forward_ios, color: Color(0xFF64748B), size: 14),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
