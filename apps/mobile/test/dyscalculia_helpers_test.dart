import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/accessibility/dyscalculia_helpers.dart';

void main() {
  group('Dyscalculia Helpers & Place-Value Tests', () {
    test('DyscalculiaPlaceValueColors maps place values correctly', () {
      expect(DyscalculiaPlaceValueColors.getColorForDigit(0), DyscalculiaPlaceValueColors.units);
      expect(DyscalculiaPlaceValueColors.getColorForDigit(1), DyscalculiaPlaceValueColors.tens);
      expect(DyscalculiaPlaceValueColors.getColorForDigit(2), DyscalculiaPlaceValueColors.hundreds);
      expect(DyscalculiaPlaceValueColors.getColorForDigit(3), DyscalculiaPlaceValueColors.thousands);
      expect(DyscalculiaPlaceValueColors.getColorForDigit(4), DyscalculiaPlaceValueColors.units); // Cyclical modulo
    });

    testWidgets('DyscalculiaNumberView renders place-value colored digits with letter-spacing 1.2', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: DyscalculiaNumberView(numberString: '425'),
          ),
        ),
      );

      final richTextFinder = find.byType(RichText);
      expect(richTextFinder, findsOneWidget);

      final richText = tester.widget<RichText>(richTextFinder);
      final textSpan = richText.text as TextSpan;
      expect(textSpan.children?.length, 3);

      // '4' is hundreds
      final span4 = textSpan.children![0] as TextSpan;
      expect(span4.text, '4');
      expect(span4.style?.color, DyscalculiaPlaceValueColors.hundreds);
      expect(span4.style?.letterSpacing, 1.2);

      // '2' is tens
      final span2 = textSpan.children![1] as TextSpan;
      expect(span2.text, '2');
      expect(span2.style?.color, DyscalculiaPlaceValueColors.tens);
      expect(span2.style?.letterSpacing, 1.2);

      // '5' is units
      final span5 = textSpan.children![2] as TextSpan;
      expect(span5.text, '5');
      expect(span5.style?.color, DyscalculiaPlaceValueColors.units);
      expect(span5.style?.letterSpacing, 1.2);
    });

    testWidgets('DyscalculiaNumberView with disabled coloring renders single Text with letter-spacing 1.2', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: DyscalculiaNumberView(
              numberString: '100',
              enablePlaceValueColoring: false,
            ),
          ),
        ),
      );

      final textFinder = find.text('100');
      expect(textFinder, findsOneWidget);
      final textWidget = tester.widget<Text>(textFinder);
      expect(textWidget.style?.letterSpacing, 1.2);
    });

    testWidgets('ColorCodedAlgebraicExpression renders tokens with letter-spacing 1.2 and distinct colors', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ColorCodedAlgebraicExpression(expression: 'x^2 + 5x - 6 = 0'),
          ),
        ),
      );

      expect(find.text('x^2'), findsOneWidget);
      expect(find.text('+'), findsOneWidget);
      expect(find.text('5x'), findsOneWidget);
      expect(find.text('-'), findsOneWidget);
      expect(find.text('6'), findsOneWidget);
      expect(find.text('='), findsOneWidget);
      expect(find.text('0'), findsOneWidget);

      final x2Text = tester.widget<Text>(find.text('x^2'));
      expect(x2Text.style?.letterSpacing, 1.2);
      expect(x2Text.style?.color, const Color(0xFF38BDF8));

      final constantText = tester.widget<Text>(find.text('6'));
      expect(constantText.style?.letterSpacing, 1.2);
      expect(constantText.style?.color, const Color(0xFF10B981));
    });

    testWidgets('VisualNumberLine renders current and target position indicators', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: VisualNumberLine(
              currentPosition: 3.0,
              targetPosition: 7.0,
            ),
          ),
        ),
      );

      expect(find.text('Konum: 3'), findsOneWidget);
      expect(find.byType(CustomPaint), findsWidgets);
    });
  });
}
