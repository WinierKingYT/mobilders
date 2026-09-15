import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/core/app_theme.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/domain/models/solution_step.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/views/zen_focus_overlay.dart';

class FakeEngineApiService extends EngineApiService {
  @override
  Future<SolutionStep> verifyStep({
    required String sessionId,
    required String nodeId,
    required int stepNumber,
    required String userExpression,
    required String targetEquation,
    String? previousStep,
    int? elapsedMs,
    double? currentPl,
    String? clientMsgId,
    DateTime? clientTimestamp,
  }) async {
    return SolutionStep(
      stepNumber: stepNumber,
      userExpression: userExpression,
      isValid: true,
      isTargetReached: false,
      elapsedMs: elapsedMs ?? 0,
    );
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late SessionViewModel viewModel;
  late TextEditingController controller;

  setUp(() {
    viewModel = SessionViewModel(
      apiService: FakeEngineApiService(),
      sessionId: 'test_zen_session',
      targetEquation: 'x^2 + 5x + 6 = 0',
      nodeId: 'N15',
    );
    controller = TextEditingController();
  });

  tearDown(() {
    controller.dispose();
  });

  Widget buildZenScreen({VoidCallback? onExit, VoidCallback? onSubmit}) {
    return MaterialApp(
      home: ZenFocusOverlay(
        viewModel: viewModel,
        inputController: controller,
        onExitZen: onExit ?? () {},
        onSubmit: onSubmit ?? () {},
      ),
    );
  }

  group('ZenFocusOverlay Widget Tests', () {
    testWidgets('Renders Zen header, target equation with math typography', (tester) async {
      await tester.pumpWidget(buildZenScreen());
      await tester.pumpAndSettle();

      expect(find.text('ZEN ODAK MODU'), findsOneWidget);
      expect(find.text('HEDEF FORMÜL'), findsOneWidget);

      // 'x^2 + 5x + 6 = 0' pretty formatted has 'x²'
      expect(find.text('x² + 5x + 6 = 0'), findsOneWidget);
    });

    testWidgets('Tapping close button triggers onExitZen callback', (tester) async {
      bool exitCalled = false;
      await tester.pumpWidget(buildZenScreen(onExit: () => exitCalled = true));
      await tester.pumpAndSettle();

      final closeBtn = find.byTooltip('Zen Modundan Çık');
      expect(closeBtn, findsOneWidget);

      await tester.tap(closeBtn);
      await tester.pumpAndSettle();

      expect(exitCalled, isTrue);
    });

    testWidgets('Past steps appear as sleek status chips', (tester) async {
      await viewModel.submitStep('x + 2 = 0');
      await tester.pumpWidget(buildZenScreen());
      await tester.pumpAndSettle();

      expect(find.text('x + 2 = 0'), findsOneWidget);
    });

    testWidgets('Live input field displays Rainbow Brackets styled preview', (tester) async {
      controller.text = '(x + 3)';
      await tester.pumpWidget(buildZenScreen());
      await tester.pumpAndSettle();

      // Find RichText displaying rainbow brackets
      final richTextFinder = find.byType(RichText);
      expect(richTextFinder, findsWidgets);
    });

    testWidgets('Touchpad in dock allows typing inside Zen mode', (tester) async {
      await tester.pumpWidget(buildZenScreen());
      await tester.pumpAndSettle();

      // Tap key 'x'
      await tester.tap(find.text('x'));
      await tester.pumpAndSettle();

      expect(controller.text, 'x');
    });
  });
}
