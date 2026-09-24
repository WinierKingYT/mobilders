import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../../data/services/mistake_vault_service.dart';
import '../../vault/mistake_autopsy_view.dart';
import '../../analytics/views/cognitive_health_atlas_screen.dart';
import '../../session/view_models/session_view_model.dart';
import '../../touchpad/math_touchpad.dart';
import '../../diagnostic/view_models/diagnostic_view_model.dart';

class CognitiveProfileHubScreen extends StatefulWidget {
  const CognitiveProfileHubScreen({super.key});

  @override
  State<CognitiveProfileHubScreen> createState() => _CognitiveProfileHubScreenState();
}

class _CognitiveProfileHubScreenState extends State<CognitiveProfileHubScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: const Key('cognitive_profile_hub_screen'),
      backgroundColor: const Color(0xFF090D16),
      appBar: AppBar(
        title: const Text(
          'Bilişsel Profil & Kasa',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFF38BDF8),
          labelColor: const Color(0xFF38BDF8),
          unselectedLabelColor: const Color(0xFF94A3B8),
          onTap: (_) => HapticFeedbackService().selectionClick(),
          tabs: const [
            Tab(
              icon: Icon(Icons.biotech_rounded, size: 20),
              text: 'Hata Kasası',
            ),
            Tab(
              icon: Icon(Icons.analytics_outlined, size: 20),
              text: 'Bilişsel Sağlık',
            ),
            Tab(
              icon: Icon(Icons.tune_rounded, size: 20),
              text: 'Ayarlar',
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          _buildProfileSummaryHeader(context),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                // Tab 1: Mistake Vault
                MistakeAutopsyView(
                  key: const Key('profile_mistake_vault_view'),
                  mistakes: MistakeVaultService.instance.mistakes,
                  onStartBossBattle: () {
                    HapticFeedbackService().stepSuccess();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Boss Battle: Zayıf konseptler üzerinde kişiselleştirilmiş mücadele başlıyor!'),
                        backgroundColor: Color(0xFFF43F5E),
                      ),
                    );
                  },
                ),

                // Tab 2: Cognitive Health Analytics (ECE, Paas, Retention)
                const CognitiveHealthAtlasScreen(),

                // Tab 3: Settings & Neurodiversity Adjustments
                _buildSettingsTab(context),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileSummaryHeader(BuildContext context) {
    DiagnosticViewModel? diagVm;
    try {
      diagVm = Provider.of<DiagnosticViewModel>(context);
    } catch (_) {}

    final bool hasProfileData = diagVm != null &&
        diagVm.seededMastery != null &&
        diagVm.seededMastery!.isNotEmpty;

    final double overallScore = hasProfileData ? diagVm.overallMasteryScore : 0.0;
    final int nodeCount = hasProfileData ? diagVm.seededMastery!.length : 0;

    return Container(
      key: const Key('profile_summary_header'),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: hasProfileData ? const Color(0xFF38BDF8).withValues(alpha: 0.3) : const Color(0xFF334155),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: hasProfileData
                  ? const Color(0xFF38BDF8).withValues(alpha: 0.15)
                  : const Color(0xFF64748B).withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(
              hasProfileData ? Icons.verified_user_rounded : Icons.person_outline_rounded,
              color: hasProfileData ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8),
              size: 22,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  hasProfileData
                      ? 'Bilişsel Ustalık Skoru: %${(overallScore * 100).toStringAsFixed(1)}'
                      : 'Bilişsel Profil: Başlangıç Seviyesi',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  hasProfileData
                      ? '$nodeCount bilişsel düğüm kalibre edildi & izleniyor'
                      : 'Henüz teşhis tamamlanmadı. İlk seansla kalibre edilecek.',
                  style: const TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          if (hasProfileData)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF10B981).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'Aktif',
                style: TextStyle(
                  color: Color(0xFF10B981),
                  fontWeight: FontWeight.bold,
                  fontSize: 11,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildSettingsTab(BuildContext context) {
    return Consumer<SessionViewModel>(
      builder: (context, sessionVm, _) {
        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text(
              'Nöroçeşitlilik & Odak Desteği',
              style: TextStyle(
                color: Color(0xFF38BDF8),
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Column(
                children: [
                  SwitchListTile(
                    value: sessionVm.isTunnelFocusMode,
                    activeThumbColor: const Color(0xFF38BDF8),
                    title: const Text(
                      'DEHB Tünel Odak Modu',
                      style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600),
                    ),
                    subtitle: const Text(
                      'Obsidyen siyahı ve yüksek kontrast ile dikkat dağıtıcı tüm dış uyaranları sıfırlar.',
                      style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                    ),
                    onChanged: (_) {
                      HapticFeedbackService().selectionClick();
                      sessionVm.toggleTunnelFocusMode();
                    },
                  ),
                  const Divider(color: Color(0xFF334155), height: 1),
                  SwitchListTile(
                    value: sessionVm.isDyscalculiaHelper,
                    activeThumbColor: const Color(0xFF10B981),
                    title: const Text(
                      'Diskalkuli Görsel Desteği',
                      style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600),
                    ),
                    subtitle: const Text(
                      'Uzamsal sayı çizgisi, basamak hizalaması ve renk kodlu cebirsel terim rozetleri.',
                      style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                    ),
                    onChanged: (_) {
                      HapticFeedbackService().selectionClick();
                      sessionVm.toggleDyscalculiaHelper();
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Girdi Yöntemi Tercihi',
              style: TextStyle(
                color: Color(0xFF38BDF8),
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              padding: const EdgeInsets.all(12),
              child: RadioGroup<InputMode>(
                groupValue: sessionVm.inputMode,
                onChanged: (mode) {
                  if (mode != null) {
                    HapticFeedbackService().modeSwitch();
                    sessionVm.setInputMode(mode);
                  }
                },
                child: const Column(
                  children: [
                    RadioListTile<InputMode>(
                      value: InputMode.touchpad,
                      activeColor: Color(0xFF38BDF8),
                      title: Text('Touchpad (Dokunmatik Matematik Tuşları)', style: TextStyle(color: Colors.white, fontSize: 13)),
                    ),
                    RadioListTile<InputMode>(
                      value: InputMode.virtualKeyboard,
                      activeColor: Color(0xFF38BDF8),
                      title: Text('Klavye / LaTeX Doğrudan Giriş', style: TextStyle(color: Colors.white, fontSize: 13)),
                    ),
                    RadioListTile<InputMode>(
                      value: InputMode.inkingCanvas,
                      activeColor: Color(0xFF38BDF8),
                      title: Text('Vektör Çizim (İnk Tuvali)', style: TextStyle(color: Colors.white, fontSize: 13)),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Müfredat & Bilişsel Model',
              style: TextStyle(
                color: Color(0xFF38BDF8),
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: const Column(
                children: [
                  ListTile(
                    leading: Icon(Icons.school_outlined, color: Color(0xFF10B981)),
                    title: Text('Müfredat Standardı', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
                    subtitle: Text('Türkiye MEB + IB Matematik Müfredatı', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                    trailing: Text('Aktif', style: TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                  Divider(color: Color(0xFF334155), height: 1),
                  ListTile(
                    leading: Icon(Icons.timer_outlined, color: Color(0xFFF59E0B)),
                    title: Text('Aralıklı Tekrar Motoru', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
                    subtitle: Text('FSRS-4.5 (Free Spaced Repetition Scheduler)', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                    trailing: Text('v4.5', style: TextStyle(color: Color(0xFFF59E0B), fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}
