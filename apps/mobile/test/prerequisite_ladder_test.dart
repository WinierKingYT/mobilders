import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/ui/features/notes/prerequisite_ladder_widget.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
  });

  const sampleChain = [
    PrerequisiteStepItem(nodeId: 'N01', title: 'Negatif Sayılar'),
    PrerequisiteStepItem(nodeId: 'N04', title: 'Lineer Denklem'),
    PrerequisiteStepItem(nodeId: 'N15', title: '2. Dereceden Denklem'),
  ];

  Widget buildTestableWidget({
    List<PrerequisiteStepItem> chain = sampleChain,
    String activeNodeId = 'N15',
    ValueChanged<String>? onSelectNode,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: PrerequisiteLadderWidget(
          chain: chain,
          activeNodeId: activeNodeId,
          onSelectNode: onSelectNode,
        ),
      ),
    );
  }

  group('PrerequisiteLadderWidget Tests', () {
    testWidgets('renders all steps with node IDs and titles', (tester) async {
      await tester.pumpWidget(buildTestableWidget());
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('prerequisite_ladder')), findsOneWidget);
      expect(find.text('Önkoşul Merdiveni'), findsOneWidget);
      expect(find.text('N01'), findsOneWidget);
      expect(find.text('Negatif Sayılar'), findsOneWidget);
      expect(find.text('N04'), findsOneWidget);
      expect(find.text('Lineer Denklem'), findsOneWidget);
      expect(find.text('N15'), findsOneWidget);
      expect(find.text('2. Dereceden Denklem'), findsOneWidget);
    });

    testWidgets('tapping a prerequisite step triggers callback and haptics', (tester) async {
      String? selected;
      await tester.pumpWidget(buildTestableWidget(
        onSelectNode: (id) => selected = id,
      ));
      await tester.pumpAndSettle();

      final stepFinder = find.byKey(const Key('ladder_step_N04'));
      expect(stepFinder, findsOneWidget);

      await tester.tap(stepFinder);
      await tester.pumpAndSettle();

      expect(selected, 'N04');
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });

    testWidgets('renders nothing if chain is empty', (tester) async {
      await tester.pumpWidget(buildTestableWidget(chain: []));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('prerequisite_ladder')), findsNothing);
    });
  });
}
