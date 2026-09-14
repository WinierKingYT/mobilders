import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/ui/features/diagnostic/view_models/diagnostic_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/views/daily_journey_screen.dart';

void main() {
  testWidgets('DailyJourneyScreen renders 20-min session header and warm-up phase', (tester) async {
    final apiService = EngineApiService();

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider<EngineApiService>.value(value: apiService),
          ChangeNotifierProvider<SessionViewModel>(
            create: (_) => SessionViewModel(
              apiService: apiService,
              sessionId: 'test-session-001',
              targetEquation: 'x^2 + 6x - 2 = 0',
            ),
          ),
          ChangeNotifierProvider<DiagnosticViewModel>(
            create: (_) => DiagnosticViewModel(
              apiService: apiService,
              sessionId: 'test-cat-001',
            ),
          ),
        ],
        child: const MaterialApp(
          home: DailyJourneyScreen(),
        ),
      ),
    );

    // Verify 20-min Header
    expect(find.text('20 Dk Günlük Bilişsel Seans'), findsOneWidget);

    // Verify Phase Stepper
    expect(find.text('1. Isınma'), findsOneWidget);
    expect(find.text('2. Teşhis'), findsOneWidget);
    expect(find.text('3. Tahta'), findsOneWidget);
    expect(find.text('4. Kapanış'), findsOneWidget);

    // Verify Initial Warmup Content
    expect(find.text('Faz 1: Bilişsel Isınma (3 Dakika)'), findsOneWidget);
    expect(find.textContaining('FSRS-4.5 aralıklı tekrar algoritması'), findsOneWidget);

    // Advance to Diagnostic Phase
    await tester.tap(find.text('Isınmayı Tamamla -> CAT Teşhise Başla'));
    await tester.pumpAndSettle();

    // Verify that the phase switched
    expect(find.text('Faz 1: Bilişsel Isınma (3 Dakika)'), findsNothing);
  });
}
