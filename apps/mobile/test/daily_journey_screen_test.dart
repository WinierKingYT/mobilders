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

  testWidgets('DailyJourneyScreen opens settings modal and shows accessibility switches', (tester) async {
    final apiService = EngineApiService();

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider<EngineApiService>.value(value: apiService),
          ChangeNotifierProvider<SessionViewModel>(
            create: (_) => SessionViewModel(
              apiService: apiService,
              sessionId: 'test-session-002',
              targetEquation: 'x^2 + 6x - 2 = 0',
            ),
          ),
          ChangeNotifierProvider<DiagnosticViewModel>(
            create: (_) => DiagnosticViewModel(
              apiService: apiService,
              sessionId: 'test-cat-002',
            ),
          ),
        ],
        child: const MaterialApp(
          home: DailyJourneyScreen(),
        ),
      ),
    );

    // Tap tune/settings icon
    await tester.tap(find.byIcon(Icons.tune_rounded));
    await tester.pumpAndSettle();

    // Verify settings modal title and options
    expect(find.text('Erişilebilirlik & Müfredat Ayarları'), findsOneWidget);
    expect(find.text('DEHB Tünel Odak Modu'), findsOneWidget);
    expect(find.text('Diskalkuli Görsel Desteği'), findsOneWidget);
    expect(find.text('Müfredat Standardı'), findsOneWidget);
    expect(find.textContaining('Türkiye MEB'), findsWidgets);
  });

  testWidgets('DailyJourneyScreen interactive warmup options give instant feedback', (tester) async {
    final apiService = EngineApiService();

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          Provider<EngineApiService>.value(value: apiService),
          ChangeNotifierProvider<SessionViewModel>(
            create: (_) => SessionViewModel(
              apiService: apiService,
              sessionId: 'test-session-003',
              targetEquation: 'x^2 + 6x - 2 = 0',
            ),
          ),
          ChangeNotifierProvider<DiagnosticViewModel>(
            create: (_) => DiagnosticViewModel(
              apiService: apiService,
              sessionId: 'test-cat-003',
            ),
          ),
        ],
        child: const MaterialApp(
          home: DailyJourneyScreen(),
        ),
      ),
    );

    // Initial state: option chips visible
    expect(find.text('x = 4'), findsOneWidget);
    expect(find.text('x = 8'), findsOneWidget);

    // Tap correct option x = 8
    await tester.tap(find.text('x = 8'));
    await tester.pumpAndSettle();

    // Verify congratulatory feedback
    expect(find.textContaining('Harika! 3(8 - 4) = 3(4) = 12'), findsOneWidget);
  });
}
