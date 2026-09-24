import 'package:flutter/material.dart';

/// Single bracket token metadata
class BracketToken {
  final int index;
  final String char;
  final int depth;
  final bool isOpening;
  final bool isMismatched;
  final Color color;

  BracketToken({
    required this.index,
    required this.char,
    required this.depth,
    required this.isOpening,
    this.isMismatched = false,
    required this.color,
  });
}

/// Comprehensive Sanity Report for Instant (<5ms) Client-Side Verification
class MathSanityReport {
  final bool isValid;
  final int unmatchedClosingCount;
  final int unclosedOpeningCount;
  final int consecutiveOperatorCount;
  final bool hasDuplicateDecimals;
  final bool hasDivisionByZero;
  final int executionTimeMicros;
  final String? errorSummary;

  const MathSanityReport({
    required this.isValid,
    required this.unmatchedClosingCount,
    required this.unclosedOpeningCount,
    required this.consecutiveOperatorCount,
    required this.hasDuplicateDecimals,
    this.hasDivisionByZero = false,
    required this.executionTimeMicros,
    this.errorSummary,
  });
}

/// Instant client-side sanitizer and Rainbow Bracket engine
class InstantMathSanitizer {
  static const List<Color> rainbowColors = [
    Color(0xFF60A5FA), // Depth 0: Sky Blue
    Color(0xFFFBBF24), // Depth 1: Amber
    Color(0xFF34D399), // Depth 2: Emerald
    Color(0xFFA78BFA), // Depth 3: Soft Purple
    Color(0xFFF472B6), // Depth 4: Rose Pink
    Color(0xFF38BDF8), // Depth 5: Cyan
  ];

  static const Color errorColor = Color(0xFFEF4444); // Error Red

  static const List<String> invisibleChars = [
    '\u200B', // zero-width space
    '\u00A0', // non-breaking space
    '\u200C', // zero-width non-joiner
    '\u200D', // zero-width joiner
    '\uFEFF', // BOM / zero-width no-break space
    '\u2060', // word joiner
  ];

  /// Strips zero-width and invisible whitespace characters.
  static String stripInvisibleChars(String text) {
    var cleaned = text;
    for (final char in invisibleChars) {
      if (char == '\u00A0') {
        cleaned = cleaned.replaceAll(char, ' ');
      } else {
        cleaned = cleaned.replaceAll(char, '');
      }
    }
    return cleaned;
  }

  /// Standardizes invisible characters and LaTeX multiplication/division operators
  static String standardizeMathExpression(String text) {
    var cleaned = stripInvisibleChars(text);
    cleaned = cleaned.replaceAll(r'\cdot', '*');
    cleaned = cleaned.replaceAll(r'\times', '*');
    cleaned = cleaned.replaceAll(r'\div', '/');
    return cleaned;
  }

  static bool isOpeningBracket(String ch) => ch == '(' || ch == '[' || ch == '{';
  static bool isClosingBracket(String ch) => ch == ')' || ch == ']' || ch == '}';
  static bool isBracket(String ch) => isOpeningBracket(ch) || isClosingBracket(ch);

  static bool isMatchingPair(String open, String close) {
    return (open == '(' && close == ')') ||
        (open == '[' && close == ']') ||
        (open == '{' && close == '}');
  }

  static bool isOperatorChar(String ch) {
    return ch == '+' ||
        ch == '-' ||
        ch == '*' ||
        ch == '/' ||
        ch == '^' ||
        ch == '=' ||
        ch == '−' ||
        ch == '–' ||
        ch == '—' ||
        ch == '×' ||
        ch == '·' ||
        ch == '•' ||
        ch == '÷';
  }

  /// Scans the expression and returns a list of bracket metadata with depths and colors.
  static List<BracketToken> scanRainbowBrackets(String text) {
    final List<BracketToken> tokens = [];
    final List<_OpenBracketRef> stack = [];

    for (int i = 0; i < text.length; i++) {
      final ch = text[i];
      if (isOpeningBracket(ch)) {
        final depth = stack.length;
        final color = rainbowColors[depth % rainbowColors.length];
        final token = BracketToken(
          index: i,
          char: ch,
          depth: depth,
          isOpening: true,
          color: color,
        );
        tokens.add(token);
        stack.add(_OpenBracketRef(token, stack.length));
      } else if (isClosingBracket(ch)) {
        if (stack.isNotEmpty && isMatchingPair(stack.last.token.char, ch)) {
          final openRef = stack.removeLast();
          final color = openRef.token.color;
          tokens.add(BracketToken(
            index: i,
            char: ch,
            depth: openRef.depth,
            isOpening: false,
            color: color,
          ));
        } else {
          // Unmatched closing bracket
          tokens.add(BracketToken(
            index: i,
            char: ch,
            depth: 0,
            isOpening: false,
            isMismatched: true,
            color: errorColor,
          ));
        }
      }
    }

    return tokens;
  }

  /// Builds a List<TextSpan> with Rainbow Brackets highlighting for RichText
  static List<TextSpan> buildRainbowSpans(
    String text, {
    TextStyle? defaultStyle,
    TextStyle? bracketBaseStyle,
  }) {
    if (text.isEmpty) return [];

    final tokens = scanRainbowBrackets(text);
    final tokenMap = <int, BracketToken>{for (var t in tokens) t.index: t};

    final List<TextSpan> spans = [];
    int start = 0;

    for (int i = 0; i < text.length; i++) {
      if (tokenMap.containsKey(i)) {
        // Add preceding text before this bracket
        if (i > start) {
          spans.add(TextSpan(
            text: text.substring(start, i),
            style: defaultStyle,
          ));
        }

        final token = tokenMap[i]!;
        spans.add(TextSpan(
          text: token.char,
          style: (bracketBaseStyle ?? defaultStyle ?? const TextStyle()).copyWith(
            color: token.color,
            fontWeight: FontWeight.bold,
            decoration: token.isMismatched ? TextDecoration.underline : null,
            decorationColor: errorColor,
          ),
        ));
        start = i + 1;
      }
    }

    if (start < text.length) {
      spans.add(TextSpan(
        text: text.substring(start),
        style: defaultStyle,
      ));
    }

    return spans;
  }

  /// Sanitizes incoming token to prevent double-operators and duplicate decimal points.
  /// Returns the replacement or appended string.
  static String sanitizeInput({
    required String currentText,
    required String incomingToken,
  }) {
    final sanitizedCurrent = stripInvisibleChars(currentText);
    var sanitizedIncoming = stripInvisibleChars(incomingToken);

    // Standardize LaTeX multiplication / division tokens
    if (sanitizedIncoming == r'\cdot' || sanitizedIncoming == r'\times') {
      sanitizedIncoming = '*';
    } else if (sanitizedIncoming == r'\div') {
      sanitizedIncoming = '/';
    }

    final trimmedCurrent = sanitizedCurrent.trimRight();
    final trimmedIncoming = sanitizedIncoming.trim();

    if (trimmedIncoming.isEmpty) return sanitizedCurrent + sanitizedIncoming;

    // Handle duplicate decimal point or comma
    if (trimmedIncoming == '.' || trimmedIncoming == ',') {
      // Find current active number token from the end
      int i = sanitizedCurrent.length - 1;
      while (i >= 0) {
        final code = sanitizedCurrent.codeUnitAt(i);
        final isDigit = code >= 48 && code <= 57; // '0'..'9'
        final isDot = code == 46 || code == 44; // '.' or ','
        if (!isDigit && !isDot) break;
        if (isDot) {
          // Already has a decimal separator in this number literal! Block duplicate
          return sanitizedCurrent;
        }
        i--;
      }
      return '$sanitizedCurrent.';
    }

    // Handle operator input (including Unicode operators)
    if (trimmedIncoming.length == 1 && isOperatorChar(trimmedIncoming)) {
      String op = trimmedIncoming;
      // Canonicalize Unicode operators to ASCII
      if (op == '−' || op == '–' || op == '—') {
        op = '-';
      } else if (op == '×' || op == '·' || op == '•') {
        op = '*';
      } else if (op == '÷') {
        op = '/';
      }

      // Empty text: only allow unary minus
      if (trimmedCurrent.isEmpty) {
        return op == '-' ? '-' : '';
      }

      // Find last non-whitespace character in currentText
      int opIndex = sanitizedCurrent.length - 1;
      while (opIndex >= 0 && sanitizedCurrent[opIndex] == ' ') {
        opIndex--;
      }

      if (opIndex < 0) {
        return op == '-' ? '-' : '';
      }

      String lastChar = sanitizedCurrent[opIndex];
      // Canonicalize lastChar for comparison
      if (lastChar == '−' || lastChar == '–' || lastChar == '—') {
        lastChar = '-';
      } else if (lastChar == '×' || lastChar == '·' || lastChar == '•') {
        lastChar = '*';
      } else if (lastChar == '÷') {
        lastChar = '/';
      }

      // After opening bracket: only allow unary minus
      if (isOpeningBracket(lastChar)) {
        return op == '-' ? '$sanitizedCurrent-' : sanitizedCurrent;
      }

      // After an existing operator
      if (isOperatorChar(lastChar)) {
        // Special case: allow multiplication, division, or equals by negative number (e.g. * -)
        if (op == '-' && (lastChar == '*' || lastChar == '/' || lastChar == '=')) {
          return sanitizedCurrent.endsWith(' ') ? '$sanitizedCurrent-' : '$sanitizedCurrent -';
        }

        // Replace the previous operator cleanly (student changed mind)
        int prefixEnd = opIndex;
        while (prefixEnd > 0 && sanitizedCurrent[prefixEnd - 1] == ' ') {
          prefixEnd--;
        }
        final prefix = sanitizedCurrent.substring(0, prefixEnd);
        return prefix.isEmpty ? (op == '-' ? '-' : '') : '$prefix $op ';
      }

      // Normal operator insertion with clean spacing
      return sanitizedCurrent.endsWith(' ') ? '$sanitizedCurrent$op ' : '$sanitizedCurrent $op ';
    }

    // Default: append incoming token
    return sanitizedCurrent + sanitizedIncoming;
  }

  /// Rapidly validates mathematical syntax sanity with execution benchmark
  static MathSanityReport validateSanity(String expression) {
    final standardized = standardizeMathExpression(expression);
    final stopwatch = Stopwatch()..start();

    int unmatchedClosing = 0;
    int unclosedOpening = 0;
    int consecutiveOps = 0;
    bool duplicateDecimals = false;

    // 1. Bracket scan
    final bracketTokens = scanRainbowBrackets(standardized);
    for (var token in bracketTokens) {
      if (token.isMismatched) unmatchedClosing++;
    }
    // Count unclosed openings
    int depthTracker = 0;
    for (var token in bracketTokens) {
      if (token.isOpening) {
        depthTracker++;
      } else if (!token.isMismatched) {
        depthTracker--;
      }
    }
    unclosedOpening = depthTracker > 0 ? depthTracker : 0;

    // 2. Scan for consecutive operators & duplicate decimals
    final cleaned = standardized.replaceAll(' ', '');
    for (int i = 0; i < cleaned.length - 1; i++) {
      final c1 = cleaned[i];
      final c2 = cleaned[i + 1];
      if (isOperatorChar(c1) && isOperatorChar(c2)) {
        // Allow unary minus after * or / or =
        if (c2 == '-' && (c1 == '*' || c1 == '/' || c1 == '=')) {
          continue;
        }
        consecutiveOps++;
      }
    }

    // Check decimal points
    final parts = standardized.split(RegExp(r'[\s+\-*/^=(),]'));
    for (var part in parts) {
      if (part.indexOf('.') != part.lastIndexOf('.')) {
        duplicateDecimals = true;
        break;
      }
    }

    // Check division by zero: e.g. / 0 or ÷ 0 or / (0)
    final hasDivisionByZero = RegExp(r'[/÷](?:\s*\(?\s*0+(?:\.0+)?\s*\)?)').hasMatch(cleaned);

    stopwatch.stop();

    final isValid = unmatchedClosing == 0 &&
        unclosedOpening == 0 &&
        consecutiveOps == 0 &&
        !duplicateDecimals &&
        !hasDivisionByZero;

    String? summary;
    if (!isValid) {
      if (hasDivisionByZero) {
        summary = 'Sıfıra bölme tanımsızdır.';
      } else if (unmatchedClosing > 0) {
        summary = '$unmatchedClosing adet kapatılmamış/hatalı parantez var.';
      } else if (unclosedOpening > 0) {
        summary = '$unclosedOpening adet açık parantez kapatılmadı.';
      } else if (consecutiveOps > 0) {
        summary = 'Ardışık çift operatör tespit edildi.';
      } else if (duplicateDecimals) {
        summary = 'Tek sayıda birden fazla ondalık nokta bulundu.';
      }
    }

    return MathSanityReport(
      isValid: isValid,
      unmatchedClosingCount: unmatchedClosing,
      unclosedOpeningCount: unclosedOpening,
      consecutiveOperatorCount: consecutiveOps,
      hasDuplicateDecimals: duplicateDecimals,
      hasDivisionByZero: hasDivisionByZero,
      executionTimeMicros: stopwatch.elapsedMicroseconds,
      errorSummary: summary,
    );
  }
}

class _OpenBracketRef {
  final BracketToken token;
  final int depth;
  _OpenBracketRef(this.token, this.depth);
}
