import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../../data/services/mistake_vault_service.dart';
import '../../vault/mistake_autopsy_view.dart';
import '../../analytics/views/cognitive_health_atlas_screen.dart';
import '../../session/view_models/session_view_model.dart';
import '../../touchpad/math_touchpad.dart';

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
      body: TabBarView(
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
