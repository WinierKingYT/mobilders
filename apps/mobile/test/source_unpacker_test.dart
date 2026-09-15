import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/source_unpacker_widget.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
  });

  group('StepSourceLineage Unit Tests', () {
    test('derives division operation correctly', () {
      final lineage = StepSourceLineage.deriveLineage(
        currentStep: 'x = 4',
        previousStep: '2x = 8',
      );
      expect(lineage.operation, contains('BÖLME'));
      expect(lineage.originFormula, '8 ÷ 2');
      expect(lineage.targetToken, '4');
      expect(lineage.explanation, contains("8 sayısı 2'ye bölünerek"));
    });

    test('derives subtraction operation correctly', () {
      final lineage = StepSourceLineage.deriveLineage(
        currentStep: '2x = 8',
        previousStep: '2x + 6 = 14',
      );
      expect(lineage.operation, contains('ÇIKARMA'));
      expect(lineage.originFormula, '14 - 6');
      expect(lineage.targetToken, '8');
      expect(lineage.explanation, contains('karşıya eksi geçerek'));
    });

    test('derives parenthesis multiplication correctly', () {
      final lineage = StepSourceLineage.deriveLineage(
        currentStep: '3x + 12 = 18',
        previousStep: '3(x + 4) = 18',
      );
      expect(lineage.operation, contains('DAĞILMA'));
      expect(lineage.originFormula, '3 × 4');
      expect(lineage.targetToken, '12');
    });
  });

  group('SourceUnpackerWidget UI Tests', () {
    Widget buildTestableWidget({
      required String currentStep,
      required String previousStep,
    }) {
      return MaterialApp(
        home: Scaffold(
          body: SourceUnpackerWidget(
            currentStep: currentStep,
            previousStep: previousStep,
          ),
        ),
      );
    }

    testWidgets('expands and displays provenance on tap', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        currentStep: 'x = 4',
        previousStep: '2x = 8',
      ));
      await tester.pumpAndSettle();

      // Initial state: header visible, details not yet expanded
      expect(find.text('Nereden Geldi Bu?'), findsOneWidget);
      expect(find.byKey(const Key('source_unpacker_content')), findsNothing);

      // Tap toggle
      final toggleFinder = find.byKey(const Key('source_unpacker_toggle'));
      await tester.tap(toggleFinder);
      await tester.pumpAndSettle();

      // Expanded state: details visible
      expect(find.byKey(const Key('source_unpacker_content')), findsOneWidget);
      expect(find.text('Köken: 8 ÷ 2'), findsOneWidget);
      expect(find.byKey(const Key('source_unpacker_explanation')), findsOneWidget);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);

      // Tap toggle again to collapse
      await tester.tap(toggleFinder);
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('source_unpacker_content')), findsNothing);
    });
  });
}
