import 'package:flutter/material.dart';
import '../../../../ui/core/app_theme.dart';

class CognitiveHealthAtlasScreen extends StatefulWidget {
  final String studentId;

  const CognitiveHealthAtlasScreen({
    super.key,
    this.studentId = 'EXP-STU-01',
  });

  @override
  State<CognitiveHealthAtlasScreen> createState() => _CognitiveHealthAtlasScreenState();
}

class _CognitiveHealthAtlasScreenState extends State<CognitiveHealthAtlasScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        title: const Text('Bilişsel Sağlık & Cebir Atlası'),
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.accentCorrect,
          labelColor: AppColors.accentCorrect,
          unselectedLabelColor: Colors.grey,
          isScrollable: true,
          tabs: const [
            Tab(icon: Icon(Icons.psychology_outlined), text: 'Metabiliş (ECE)'),
            Tab(icon: Icon(Icons.speed), text: 'Paas Bilişsel Yük'),
            Tab(icon: Icon(Icons.timeline), text: 'FSRS 14 Gün Kalıcılık'),
            Tab(icon: Icon(Icons.account_tree_outlined), text: '26 Düğüm Atlası'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildMetacognitiveTab(),
          _buildPaasEfficiencyTab(),
          _buildRetentionTab(),
          _buildAtlasTopologyTab(),
        ],
      ),
    );
  }

  Widget _buildMetacognitiveTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildMetricCard(
            title: 'Beklenen Kalibrasyon Hatası (ECE)',
            value: '0.0661',
            status: 'YÜKSEK ÜSTBİLİŞSEL KALİBRASYON (ECE ≤ 0.10)',
            statusColor: AppColors.accentCorrect,
            description:
                'Öğrencinin kendi bilgisine duyduğu güven ile gerçek test başarısı arasındaki sapma %6.6 seviyesindedir. Aşırı özgüven veya imposter sendromu giderilmiştir.',
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSmallCard(
                  label: 'Brier Skoru',
                  value: '0.048',
                  sub: 'Mükemmel (0.0’a yakın)',
                  icon: Icons.check_circle_outline,
                  color: AppColors.accentCorrect,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildSmallCard(
                  label: 'İmposter Oranı',
                  value: '%4.2',
                  sub: 'Düşük Sahte Şüphe',
                  icon: Icons.verified_user_outlined,
                  color: Colors.blueAccent,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Text(
            'Güven vs. Gerçek Doğruluk Dağılımı (Reliability Diagram)',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black26,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white12),
            ),
            child: Column(
              children: [
                _buildReliabilityBar('0.0 - 0.2 Güven Aralığı', 0.18, 0.15),
                _buildReliabilityBar('0.2 - 0.4 Güven Aralığı', 0.32, 0.30),
                _buildReliabilityBar('0.4 - 0.6 Güven Aralığı', 0.52, 0.50),
                _buildReliabilityBar('0.6 - 0.8 Güven Aralığı', 0.74, 0.70),
                _buildReliabilityBar('0.8 - 1.0 Güven Aralığı', 0.91, 0.88),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPaasEfficiencyTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildMetricCard(
            title: 'Paas Bilişsel Verimlilik İndeksi (E)',
            value: '+0.752',
            status: 'YÜKSEK BİLİŞSEL VERİM (AKIŞ DURUMU)',
            statusColor: AppColors.accentCorrect,
            description:
                'Paas & Van Merriënboer formülü: E = (z_P - z_R) / √2. Düşük zihinsel sürtünme ve yüksek doğruluk akıcı ustalık bölgesini doğrulamaktadır.',
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildSmallCard(
                  label: 'Ortalama Tepki Süresi',
                  value: '3.12 s',
                  sub: 'Akıcı İcra Bandı',
                  icon: Icons.timer_outlined,
                  color: Colors.amber,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildSmallCard(
                  label: 'Ratcliff DDM Hızı (v)',
                  value: '0.184',
                  sub: 'Enformasyon Sürüklenmesi',
                  icon: Icons.bolt,
                  color: AppColors.accentCorrect,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Text(
            'Paas 2D Bilişsel Düzlemi (Zihinsel Çaba vs. Performans)',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white),
          ),
          const SizedBox(height: 12),
          Container(
            height: 180,
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black26,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white12),
            ),
            child: Stack(
              children: [
                Center(
                  child: Container(
                    height: 1,
                    color: Colors.white24,
                  ),
                ),
                Center(
                  child: Container(
                    width: 1,
                    color: Colors.white24,
                  ),
                ),
                const Positioned(
                  top: 8,
                  left: 8,
                  child: Text('Yüksek Verimlilik (E > 0)', style: TextStyle(color: Colors.greenAccent, fontSize: 11)),
                ),
                const Positioned(
                  bottom: 8,
                  right: 8,
                  child: Text('Aşırı Yüklenme (E < 0)', style: TextStyle(color: Colors.redAccent, fontSize: 11)),
                ),
                Positioned(
                  top: 35,
                  right: 90,
                  child: Row(
                    children: [
                      Container(
                        width: 14,
                        height: 14,
                        decoration: const BoxDecoration(
                          color: AppColors.accentCorrect,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 6),
                      const Text('Öğrenci Konumu (E=+0.75)', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
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

  Widget _buildRetentionTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildMetricCard(
            title: '14 Günlük Hatırlama Kalıcılığı S(14)',
            value: '%86.7',
            status: 'FSRS-4.5 DSR KALICILIK MODELİ',
            statusColor: AppColors.accentCorrect,
            description:
                'Walker & Stickgold sirkadiyen uyku konsolidasyonu ve 14 saatlik yığın çalışma kilidi sayesinde 14 gün sonra beklenen kalıcı hatırlama %86.7 olarak projekte edilmektedir.',
          ),
          const SizedBox(height: 16),
          _buildSmallCard(
            label: 'Ortalama Bellek Kararlılığı (S)',
            value: '18.25 Gün',
            sub: 'DSR Kararlılık Parametresi',
            icon: Icons.calendar_today,
            color: Colors.cyanAccent,
          ),
          const SizedBox(height: 20),
          const Text(
            '14 Günlük Unutma Eğrisi ve Hatırlanabilirlik R(t, S)',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black26,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white12),
            ),
            child: Column(
              children: [
                _buildRetentionRow('1. Gün', 0.98),
                _buildRetentionRow('3. Gün', 0.95),
                _buildRetentionRow('7. Gün', 0.91),
                _buildRetentionRow('10. Gün', 0.89),
                _buildRetentionRow('14. Gün (Hedef Baraj)', 0.867),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAtlasTopologyTab() {
    final groups = [
      {'title': 'Seviye 0: Temel Cebir & Aritmetik', 'nodes': ['N01', 'N02', 'N03', 'N04'], 'mastered': true},
      {'title': 'Seviye 1: Çarpanlara Ayırma', 'nodes': ['N05', 'N06', 'N07', 'N08', 'N09'], 'mastered': true},
      {'title': 'Seviye 2: İkinci Dereceden Temeller', 'nodes': ['N10', 'N11', 'N12', 'N13'], 'mastered': true},
      {'title': 'Seviye 3: Tam Kare & Alan Modeli', 'nodes': ['N14', 'N15', 'N16'], 'mastered': true},
      {'title': 'Seviye 4: Formül & Diskriminant', 'nodes': ['N17', 'N18', 'N19', 'N20'], 'mastered': true},
      {'title': 'Seviye 5 (Grup A): İkinci Dereceden Eşitsizlikler', 'nodes': ['N21', 'N22', 'N23'], 'mastered': false, 'zpd': 'N23'},
      {'title': 'Seviye 5 (Grup B): Parabol & Dönüşümler', 'nodes': ['N24', 'N25', 'N26'], 'mastered': false, 'zpd': 'N25'},
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16.0),
      itemCount: groups.length,
      itemBuilder: (context, idx) {
        final g = groups[idx];
        final bool isAllMastered = g['mastered'] as bool;
        final String? zpdNode = g['zpd'] as String?;
        final nodes = g['nodes'] as List<String>;

        return Card(
          color: Colors.black26,
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: isAllMastered ? AppColors.accentCorrect : Colors.white12,
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      isAllMastered ? Icons.check_circle : Icons.pending_outlined,
                      color: isAllMastered ? AppColors.accentCorrect : Colors.orangeAccent,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        g['title'] as String,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  runSpacing: 6,
                  children: nodes.map((n) {
                    final isZpd = n == zpdNode;
                    final isNodeMastered = isAllMastered || n == 'N21' || n == 'N22' || n == 'N24';
                    return Chip(
                      label: Text(
                        n,
                        style: TextStyle(
                          color: isNodeMastered ? Colors.white : (isZpd ? Colors.black : Colors.grey),
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                      backgroundColor: isNodeMastered
                          ? AppColors.accentCorrect
                          : (isZpd ? Colors.orangeAccent : Colors.white10),
                      avatar: isNodeMastered
                          ? const Icon(Icons.check, size: 14, color: Colors.white)
                          : (isZpd ? const Icon(Icons.arrow_forward, size: 14, color: Colors.black) : const Icon(Icons.lock_outline, size: 14, color: Colors.grey)),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildMetricCard({
    required String title,
    required String value,
    required String status,
    required Color statusColor,
    required String description,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.black26,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: statusColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          const SizedBox(height: 6),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: statusColor,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(status, style: const TextStyle(color: Colors.black, fontSize: 11, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 10),
          Text(description, style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildSmallCard({
    required String label,
    required String value,
    required String sub,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.black26,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 18),
              const SizedBox(width: 6),
              Expanded(child: Text(label, style: const TextStyle(color: Colors.grey, fontSize: 11))),
            ],
          ),
          const SizedBox(height: 6),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(sub, style: TextStyle(color: color, fontSize: 10)),
        ],
      ),
    );
  }

  Widget _buildReliabilityBar(String range, double actual, double confidence) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(width: 140, child: Text(range, style: const TextStyle(color: Colors.white70, fontSize: 11))),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: actual,
                minHeight: 10,
                backgroundColor: Colors.white10,
                valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accentCorrect),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Text('%${(actual * 100).toStringAsFixed(0)}', style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildRetentionRow(String day, double probability) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        children: [
          SizedBox(width: 120, child: Text(day, style: const TextStyle(color: Colors.white70, fontSize: 12))),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: probability,
                minHeight: 10,
                backgroundColor: Colors.white10,
                valueColor: const AlwaysStoppedAnimation<Color>(Colors.cyanAccent),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Text('%${(probability * 100).toStringAsFixed(1)}', style: const TextStyle(color: Colors.cyanAccent, fontSize: 12, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
