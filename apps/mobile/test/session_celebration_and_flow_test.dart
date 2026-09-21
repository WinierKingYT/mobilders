import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/session_restoration_manager.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/views/session_screen.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('SessionScreen renders celebration banner with twin button when target reached', (tester) async {
    final apiService = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
    final vm = SessionViewModel(
      apiService: apiService,
      sessionId: 'test-session-celebration',
      targetEquation: 'x^2 - 4 = 0',
    );

    await tester.pumpWidget(
      ChangeNotifierProvider<SessionViewModel>.value(
        value: vm,
        child: const MaterialApp(
          home: SessionScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Initially target not reached
    expect(find.byKey(const Key('target_reached_celebration_banner')), findsNothing);

    // Simulate step that reaches target
    vm.loadFromRestoredState(
      RestoredSessionState(
        sessionId: 'test-session-celebration',
        nodeId: 'N15',
        targetEquation: 'x^2 - 4 = 0',
        draftText: '',
        inputMode: InputMode.touchpad,
        currentPl: 0.85,
        lastUpdated: DateTime.now(),
        serializedSteps: [
          {
            'step_number': 1,
            'user_expression': 'x = 2',
            'is_valid': true,
            'is_target_reached': true,
            'elapsed_ms': 450,
          }
        ],
      ),
    );
    await tester.pumpAndSettle();

    // Celebration banner should now be visible
    expect(find.byKey(const Key('target_reached_celebration_banner')), findsOneWidget);
    expect(find.text('Tebrikler! Denklem Çözüldü.'), findsOneWidget);
    expect(find.byKey(const Key('celebration_twin_practice_button')), findsOneWidget);
    expect(find.byKey(const Key('celebration_next_target_button')), findsOneWidget);

    // Tap twin practice button in celebration banner
    await tester.tap(find.byKey(const Key('celebration_twin_practice_button')));
    await tester.pumpAndSettle();

    // Verify session updated to a twin equation
    expect(vm.targetEquation.isNotEmpty, true);
    expect(vm.isTargetReached, false);
  });

  testWidgets('Tapping celebration_next_target_button resets the session', (tester) async {
    final apiService = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
    final vm = SessionViewModel(
      apiService: apiService,
      sessionId: 'test-session-celebration-reset',
      targetEquation: 'x^2 = 9',
    );

    await tester.pumpWidget(
      ChangeNotifierProvider<SessionViewModel>.value(
        value: vm,
        child: const MaterialApp(
          home: SessionScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    vm.loadFromRestoredState(
      RestoredSessionState(
        sessionId: 'test-session-celebration-reset',
        nodeId: 'N15',
        targetEquation: 'x^2 = 9',
        draftText: '',
        inputMode: InputMode.touchpad,
        currentPl: 0.90,
        lastUpdated: DateTime.now(),
        serializedSteps: [
          {
            'step_number': 1,
            'user_expression': 'x = 3',
            'is_valid': true,
            'is_target_reached': true,
            'elapsed_ms': 300,
          }
        ],
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('target_reached_celebration_banner')), findsOneWidget);

    // Tap reset button
    await tester.tap(find.byKey(const Key('celebration_next_target_button')));
    await tester.pumpAndSettle();

    expect(vm.steps.isEmpty, true);
    expect(vm.isTargetReached, false);
    expect(find.byKey(const Key('target_reached_celebration_banner')), findsNothing);
  });
}
