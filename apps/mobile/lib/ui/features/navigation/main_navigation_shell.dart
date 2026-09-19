import 'package:flutter/material.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../session/views/daily_journey_screen.dart';
import '../atlas/living_knowledge_atlas_view.dart';
import '../math_lab/views/math_lab_hub_screen.dart';
import '../profile/views/cognitive_profile_hub_screen.dart';

class MainNavigationShell extends StatefulWidget {
  final int initialIndex;

  const MainNavigationShell({
    super.key,
    this.initialIndex = 0,
  });

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
  }

  void _onTabSelected(int index) {
    if (_currentIndex == index) return;
    HapticFeedbackService().selectionClick();
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: const Key('main_navigation_shell'),
      backgroundColor: const Color(0xFF090D16),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          DailyJourneyScreen(
            onNavigateToTab: _onTabSelected,
          ),
          const Scaffold(
            backgroundColor: Color(0xFF090D16),
            body: SafeArea(child: LivingKnowledgeAtlasView()),
          ),
          const MathLabHubScreen(),
          const CognitiveProfileHubScreen(),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Color(0xFF0F172A),
          border: Border(
            top: BorderSide(color: Color(0xFF1E293B), width: 1),
          ),
        ),
        child: NavigationBar(
          selectedIndex: _currentIndex,
          onDestinationSelected: _onTabSelected,
          backgroundColor: const Color(0xFF0F172A),
          indicatorColor: const Color(0xFF38BDF8).withValues(alpha: 0.2),
          elevation: 0,
          destinations: const [
            NavigationDestination(
              key: Key('nav_tab_daily'),
              icon: Icon(Icons.timer_outlined, color: Color(0xFF94A3B8)),
              selectedIcon: Icon(Icons.timer, color: Color(0xFF38BDF8)),
              label: 'Günlük Seans',
            ),
            NavigationDestination(
              key: Key('nav_tab_atlas'),
              icon: Icon(Icons.hub_outlined, color: Color(0xFF94A3B8)),
              selectedIcon: Icon(Icons.hub, color: Color(0xFF10B981)),
              label: 'Zihin Atlası',
            ),
            NavigationDestination(
              key: Key('nav_tab_math_lab'),
              icon: Icon(Icons.architecture_outlined, color: Color(0xFF94A3B8)),
              selectedIcon: Icon(Icons.architecture, color: Color(0xFFF59E0B)),
              label: 'Matematik Lab',
            ),
            NavigationDestination(
              key: Key('nav_tab_profile'),
              icon: Icon(Icons.person_outline, color: Color(0xFF94A3B8)),
              selectedIcon: Icon(Icons.person, color: Color(0xFFF43F5E)),
              label: 'Bilişsel Profil',
            ),
          ],
        ),
      ),
    );
  }
}
