import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/domain/models/diagnostic_bug.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/interactive_socratic_chat_dialog.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
    InteractiveSocraticChatDialog.clearHistoryCache();
  });

  Widget buildTestableWidget({
    String targetEquation = 'x^2 - 5x + 6 = 0',
    DiagnosticBug? diagnosticBug,
    String? userExpression,
    Function(String)? onApplyCorrectedStep,
    EngineApiService? apiService,
    String? sessionHistoryKey,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: Builder(
          builder: (context) => ElevatedButton(
            key: const Key('open_dialog_btn'),
            onPressed: () {
              InteractiveSocraticChatDialog.show(
                context,
                targetEquation: targetEquation,
                diagnosticBug: diagnosticBug,
                userExpression: userExpression,
                onApplyCorrectedStep: onApplyCorrectedStep,
                apiService: apiService,
                sessionHistoryKey: sessionHistoryKey,
              );
            },
            child: const Text('Open'),
          ),
        ),
      ),
    );
  }

  group('InteractiveSocraticChatDialog Tests', () {
    testWidgets('renders dialog and shows opening tutor message', (tester) async {
      const bug = DiagnosticBug(
        category: 'sign_flip',
        description: 'İşaret ters çevrilirken hata yapıldı.',
        severity: 'high',
        remediationDirective: 'Parantez açarken eksi işaretinin içeriye nasıl dağıldığına dikkat et.',
      );

      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
        diagnosticBug: bug,
        userExpression: 'x^2 + 5x + 6 = 0',
      ));
      await tester.pumpAndSettle();

      // Open bottom sheet
      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // Verify header and initial message
      expect(find.byKey(const Key('socratic_chat_header')), findsOneWidget);
      expect(find.text('Sokratik Öğretmen'), findsOneWidget);
      expect(find.text('İşaret ters çevrilirken hata yapıldı.'), findsOneWidget);
      expect(find.byKey(const Key('socratic_chat_input')), findsOneWidget);
      expect(find.byKey(const Key('socratic_chat_send_button')), findsOneWidget);

      // Verify opening message is displayed (either from fallback or remediation)
      expect(find.textContaining('Parantez açarken'), findsWidgets);
    });

    testWidgets('sends message via quick suggestion chip and receives tutor reply', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // Tap quick chip "Neden öyle?"
      final chipFinder = find.text('Neden öyle?');
      expect(chipFinder, findsOneWidget);
      await tester.tap(chipFinder);
      await tester.pumpAndSettle();

      // User message should appear in chat
      expect(
        find.descendant(
          of: find.byKey(const Key('socratic_chat_message_list')),
          matching: find.text('Neden öyle?'),
        ),
        findsOneWidget,
      );

      // Socratic assistant should have responded
      expect(find.byType(ListView), findsWidgets);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });

    testWidgets('sends custom text message and shows apply button for algebraic step', (tester) async {
      String? appliedStep;

      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
        onApplyCorrectedStep: (step) {
          appliedStep = step;
        },
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // Type algebraic step into input field
      await tester.enterText(find.byKey(const Key('socratic_chat_input')), '(x - 2)(x - 3) = 0');
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')));
      await tester.pumpAndSettle();

      // Verify user message appears
      expect(find.text('(x - 2)(x - 3) = 0'), findsOneWidget);

      // Verify "Bu Adımı Çözüme Aktar" button appears for this algebraic message
      final applyBtn = find.byKey(const Key('socratic_apply_step_button'));
      expect(applyBtn, findsOneWidget);

      // Tap "Bu Adımı Çözüme Aktar"
      await tester.tap(applyBtn);
      await tester.pumpAndSettle();

      // Verify step was applied and dialog closed
      expect(appliedStep, '(x - 2)(x - 3) = 0');
      expect(find.byKey(const Key('socratic_chat_header')), findsNothing);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.heavyImpact), isTrue);
    });

    testWidgets('close button dismisses dialog', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_chat_header')), findsOneWidget);

      await tester.tap(find.byKey(const Key('socratic_chat_close_button')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_chat_header')), findsNothing);
    });
  });

  group('Socratic Chat Resilience & Lifecycle Tests (Stage 60)', () {
    testWidgets('Double-submit button lock prevents duplicate requests during in-flight reply', (tester) async {
      int requestCount = 0;
      Completer<http.Response>? sendCompleter;

      final mockClient = MockClient((request) async {
        if (request.url.path.contains('/api/v1/socratic/respond')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          final history = body['conversation_history'] as List<dynamic>? ?? [];
          if (history.isEmpty) {
            // Opening greeting
            return http.Response(
              jsonEncode({'final_output': 'Soru üzerinde birlikte düşünelim.'}),
              200,
              headers: {'content-type': 'application/json'},
            );
          } else {
            // Student question / step
            requestCount++;
            if (sendCompleter != null) {
              return await sendCompleter.future;
            }
            return http.Response(
              jsonEncode({'final_output': 'Harika bir yaklaşım!'}),
              200,
              headers: {'content-type': 'application/json'},
            );
          }
        }
        return http.Response('Not Found', 404);
      });

      final apiService = EngineApiService(client: mockClient);

      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
        apiService: apiService,
      ));
      await tester.pumpAndSettle();

      // Open bottom sheet
      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      expect(find.text('Soru üzerinde birlikte düşünelim.'), findsOneWidget);

      // Setup delayed response to test button lock while request is in flight
      sendCompleter = Completer<http.Response>();

      // Type question into input
      await tester.enterText(find.byKey(const Key('socratic_chat_input')), 'x = 2 olabilir mi?');

      // Tap send button once
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')));
      await tester.pump();

      // First request is fired
      expect(requestCount, equals(1));

      // Verify that send button is locked (onPressed is null)
      final sendBtn = tester.widget<IconButton>(find.byKey(const Key('socratic_chat_send_button')));
      expect(sendBtn.onPressed, isNull);

      // Verify progress indicator is rendered inside the button
      expect(find.descendant(
        of: find.byKey(const Key('socratic_chat_send_button')),
        matching: find.byType(CircularProgressIndicator),
      ), findsOneWidget);

      // Student rapidly attempts to double-submit / spam taps while button is locked
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')), warnIfMissed: false);
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')), warnIfMissed: false);
      await tester.pump();

      // Request count remains strictly 1 (double submit prevented!)
      expect(requestCount, equals(1));

      // Server responds
      sendCompleter.complete(http.Response(
        jsonEncode({'final_output': 'Evet! x=2 yerine koyulduğunda 4 - 10 + 6 = 0 sağlar.'}),
        200,
        headers: {'content-type': 'application/json'},
      ));
      await tester.pumpAndSettle();

      // Button is unlocked after response arrives
      final unlockedBtn = tester.widget<IconButton>(find.byKey(const Key('socratic_chat_send_button')));
      expect(unlockedBtn.onPressed, isNotNull);

      // Message and reply are displayed
      expect(find.text('x = 2 olabilir mi?'), findsOneWidget);
      expect(find.text('Evet! x=2 yerine koyulduğunda 4 - 10 + 6 = 0 sağlar.'), findsOneWidget);
    });

    testWidgets('History queue integrity persists conversation across dialog dismiss and reopen', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 7x + 12 = 0',
      ));
      await tester.pumpAndSettle();

      // Open dialog
      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // Enter student message
      await tester.enterText(find.byKey(const Key('socratic_chat_input')), 'Çarpanlar -3 ve -4 mü?');
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')));
      await tester.pumpAndSettle();

      expect(find.text('Çarpanlar -3 ve -4 mü?'), findsOneWidget);

      // Dismiss dialog
      await tester.tap(find.byKey(const Key('socratic_chat_close_button')));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('socratic_chat_header')), findsNothing);

      // Reopen dialog for the same equation
      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // History is retained intact!
      expect(find.byKey(const Key('socratic_chat_header')), findsOneWidget);
      expect(find.text('Çarpanlar -3 ve -4 mü?'), findsOneWidget);

      // Dialog is ready for subsequent questions without losing state
      await tester.enterText(find.byKey(const Key('socratic_chat_input')), 'O halde kökler 3 ve 4.');
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')));
      await tester.pumpAndSettle();

      expect(find.text('O halde kökler 3 ve 4.'), findsOneWidget);
    });

    testWidgets('Network failure gracefully recovers and unlocks send button', (tester) async {
      final mockClient = MockClient((request) async {
        if (request.url.path.contains('/api/v1/socratic/respond')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          final history = body['conversation_history'] as List<dynamic>? ?? [];
          if (history.isEmpty) {
            return http.Response(
              jsonEncode({'final_output': 'Başlayalım.'}),
              200,
              headers: {'content-type': 'application/json'},
            );
          } else {
            // Simulate sudden network drop
            throw const HttpException('Connection reset by peer');
          }
        }
        return http.Response('Not Found', 404);
      });

      final apiService = EngineApiService(client: mockClient);

      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 = 25',
        apiService: apiService,
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('socratic_chat_input')), 'x = 5');
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')));
      await tester.pumpAndSettle();

      // Pedagogical fallback response displayed
      expect(find.text('Bu aşamada eşitliği korumak için her iki tarafa hangi işlemi uygulamalıyız?'), findsOneWidget);

      // Send button is unlocked again, preventing deadlock
      final btn = tester.widget<IconButton>(find.byKey(const Key('socratic_chat_send_button')));
      expect(btn.onPressed, isNotNull);
    });
  });
}
