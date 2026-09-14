import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'data/services/engine_api_service.dart';
import 'ui/core/app_theme.dart';
import 'ui/features/session/view_models/session_view_model.dart';
import 'ui/features/session/views/session_screen.dart';

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
            targetEquation: 'x^2 - 5x + 6 = 0',
            nodeId: 'N15',
            initialPl: 0.20,
          ),
          update: (ctx, apiService, previous) =>
              previous ??
              SessionViewModel(
                apiService: apiService,
                sessionId: 'mobile-dev-session-001',
                targetEquation: 'x^2 - 5x + 6 = 0',
                nodeId: 'N15',
                initialPl: 0.20,
              ),
        ),
      ],
      child: MaterialApp(
        title: 'Kişisel Öğrenme Motoru',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: const SessionScreen(),
      ),
    );
  }
}
