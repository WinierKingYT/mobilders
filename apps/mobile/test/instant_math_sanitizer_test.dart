import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/touchpad/instant_math_sanitizer.dart';

void main() {
  group('InstantMathSanitizer Tests', () {
    test('Single bracket pair gets depth 0 and primary rainbow color', () {
      final tokens = InstantMathSanitizer.scanRainbowBrackets('(x + 2)');
      expect(tokens.length, 2);

      expect(tokens[0].char, '(');
      expect(tokens[0].depth, 0);
      expect(tokens[0].color, InstantMathSanitizer.rainbowColors[0]);
      expect(tokens[0].isMismatched, isFalse);

      expect(tokens[1].char, ')');
      expect(tokens[1].depth, 0);
      expect(tokens[1].color, InstantMathSanitizer.rainbowColors[0]);
      expect(tokens[1].isMismatched, isFalse);
    });

    test('Nested brackets receive incremented depths and distinct colors', () {
      final tokens = InstantMathSanitizer.scanRainbowBrackets('((x + 1) * [y - 2])');
      expect(tokens.length, 6);

      // Outer '('
      expect(tokens[0].depth, 0);
      expect(tokens[0].color, InstantMathSanitizer.rainbowColors[0]);

      // Inner '('
      expect(tokens[1].depth, 1);
      expect(tokens[1].color, InstantMathSanitizer.rainbowColors[1]);

      // Inner ')'
      expect(tokens[2].depth, 1);
      expect(tokens[2].color, InstantMathSanitizer.rainbowColors[1]);

      // Inner '['
      expect(tokens[3].depth, 1);
      expect(tokens[3].color, InstantMathSanitizer.rainbowColors[1]);

      // Inner ']'
      expect(tokens[4].depth, 1);
      expect(tokens[4].color, InstantMathSanitizer.rainbowColors[1]);

      // Outer ')'
      expect(tokens[5].depth, 0);
      expect(tokens[5].color, InstantMathSanitizer.rainbowColors[0]);
    });

    test('Unmatched closing bracket is flagged as mismatched with errorColor', () {
      final tokens = InstantMathSanitizer.scanRainbowBrackets('x + 3)');
      expect(tokens.length, 1);
      expect(tokens[0].isMismatched, isTrue);
      expect(tokens[0].color, InstantMathSanitizer.errorColor);
    });

    test('buildRainbowSpans generates styled spans with rainbow colors', () {
      final spans = InstantMathSanitizer.buildRainbowSpans('(2x + 1)');
      expect(spans.length, 3); // '(', '2x + 1', ')'
      expect(spans[0].text, '(');
      expect(spans[0].style?.color, InstantMathSanitizer.rainbowColors[0]);
      expect(spans[1].text, '2x + 1');
      expect(spans[2].text, ')');
      expect(spans[2].style?.color, InstantMathSanitizer.rainbowColors[0]);
    });

    test('Double operator input replaces previous operator cleanly', () {
      final current = '2x + ';
      final sanitized = InstantMathSanitizer.sanitizeInput(
        currentText: current,
        incomingToken: '-',
      );
      expect(sanitized, '2x - ');
    });

    test('Unary minus is allowed after opening parenthesis or multiplication', () {
      final afterParen = InstantMathSanitizer.sanitizeInput(
        currentText: '(',
        incomingToken: '-',
      );
      expect(afterParen, '(-');

      final afterMult = InstantMathSanitizer.sanitizeInput(
        currentText: '3 * ',
        incomingToken: '-',
      );
      expect(afterMult, '3 * -');
    });

    test('Duplicate decimal point in the same number token is blocked', () {
      final once = InstantMathSanitizer.sanitizeInput(
        currentText: '3.',
        incomingToken: '1',
      );
      expect(once, '3.1');

      final blockedDot = InstantMathSanitizer.sanitizeInput(
        currentText: '3.14',
        incomingToken: '.',
      );
      expect(blockedDot, '3.14'); // Dot rejected!
    });

    test('validateSanity executes in < 5ms even for large 500-char equations', () {
      final largeMath = List.generate(25, (i) => '((x + $i) * (y - $i))').join(' + ');
      expect(largeMath.length, greaterThan(400));

      final report = InstantMathSanitizer.validateSanity(largeMath);
      expect(report.isValid, isTrue);
      expect(report.unmatchedClosingCount, 0);
      expect(report.unclosedOpeningCount, 0);
      // Execution time must be < 5000 microseconds (5ms)
      expect(report.executionTimeMicros, lessThan(5000));
    });
  });
}
