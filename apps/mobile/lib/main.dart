import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'data/services/engine_api_service.dart';
import 'ui/core/app_theme.dart';
import 'ui/features/session/view_models/session_view_model.dart';
import 'ui/features/session/views/daily_journey_screen.dart';
import 'ui/features/diagnostic/view_models/diagnostic_view_model.dart';
import 'ui/features/navigation/main_navigation_shell.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const PersonalLearningEngineApp());
}

class PersonalLearningEngineApp extends StatelessWidget {
  const PersonalLearningEngineApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<EngineApiService>(
          create: (_) => EngineApiService(),
          dispose: (_, service) => service.dispose(),
        ),
        ChangeNotifierProxyProvider<EngineApiService, SessionViewModel>(
          create: (ctx) => SessionViewModel(
            apiService: ctx.read<EngineApiService>(),
            sessionId: 'mobile-dev-session-001',
            targetEquation: 'x^2 + 6x - 2 = 0',
            nodeId: 'N15',
            initialPl: 0.20,
          ),
          update: (ctx, apiService, previous) =>
              previous ??
              SessionViewModel(
                apiService: apiService,
                sessionId: 'mobile-dev-session-001',
                targetEquation: 'x^2 + 6x - 2 = 0',
                nodeId: 'N15',
                initialPl: 0.20,
              ),
        ),
        ChangeNotifierProxyProvider<EngineApiService, DiagnosticViewModel>(
          create: (ctx) => DiagnosticViewModel(
            apiService: ctx.read<EngineApiService>(),
            sessionId: 'mobile-dev-cat-001',
          ),
          update: (ctx, apiService, previous) =>
              previous ??
              DiagnosticViewModel(
                apiService: apiService,
                sessionId: 'mobile-dev-cat-001',
              ),
        ),
      ],
      child: MaterialApp(
        title: 'Kişisel Öğrenme Motoru',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: const MainNavigationShell(),
      ),
    );
  }
}
