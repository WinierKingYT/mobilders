import 'package:flutter/material.dart';

class AppColors {
  static const Color bgPrimary = Color(0xFF0F172A);      // Slate 900
  static const Color bgSurface = Color(0xFF1E293B);      // Slate 800
  static const Color bgCard = Color(0xFF334155);         // Slate 700
  static const Color accentPrimary = Color(0xFF6366F1);  // Indigo 500
  static const Color accentCorrect = Color(0xFF10B981);  // Emerald 500
  static const Color accentWarning = Color(0xFFF59E0B);  // Amber 500
  static const Color accentError = Color(0xFFEF4444);    // Rose 500
  static const Color textPrimary = Color(0xFFF8FAFC);    // Slate 50
  static const Color textSecondary = Color(0xFF94A3B8);  // Slate 400
  static const Color textMuted = Color(0xFF64748B);      // Slate 500
  static const Color touchpadKeyBg = Color(0xFF1E293B);
  static const Color touchpadKeyText = Color(0xFFF1F5F9);
  static const Color touchpadOpBg = Color(0xFF2E3D52);
  static const Color touchpadActionBg = Color(0xFF4F46E5);

  // Zen Mode Palette
  static const Color zenBg = Color(0xFF080C14);         // Deep obsidian
  static const Color zenSurface = Color(0xFF111827);    // Dark slate card
  static const Color zenGlow = Color(0xFF38BDF8);       // Cyan focus glow

  // Pure AMOLED Siyah Palette (#000000)
  static const Color amoledBg = Color(0xFF000000);       // True black (0W OLED draw)
  static const Color amoledSurface = Color(0xFF0A0A0A);  // Deep contrast surface
  static const Color amoledCard = Color(0xFF141414);     // Deep card
}

class MathTypography {
  static const TextStyle formulaDisplay = TextStyle(
    fontFamily: 'monospace',
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Color(0xFFF8FAFC),
    letterSpacing: 1.2,
    height: 1.3,
  );

  static const TextStyle formulaActiveStep = TextStyle(
    fontFamily: 'monospace',
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: Color(0xFF38BDF8),
    letterSpacing: 1.0,
  );

  static const TextStyle dyscalculiaMath = TextStyle(
    fontFamily: 'monospace',
    fontSize: 22,
    fontWeight: FontWeight.bold,
    color: Color(0xFFF8FAFC),
    letterSpacing: 1.2,
    height: 1.4,
  );

  static const TextStyle stepAnnotation = TextStyle(
    fontSize: 13,
    color: Color(0xFF94A3B8),
    fontStyle: FontStyle.italic,
  );

  /// Converts ASCII math shortcuts into beautiful Unicode typography
  static String toPrettyMath(String raw) {
    return raw
        .replaceAll('+-', '±')
        .replaceAll('x^2', 'x²')
        .replaceAll('x^3', 'x³')
        .replaceAll('x^4', 'x⁴')
        .replaceAll('sqrt(', '√(')
        .replaceAll('*', '×')
        .replaceAll('/', '÷');
  }
}

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.bgPrimary,
      cardColor: AppColors.bgSurface,
      colorScheme: const ColorScheme.dark(
        primary: AppColors.accentPrimary,
        secondary: AppColors.accentCorrect,
        surface: AppColors.bgSurface,
        error: AppColors.accentError,
      ),
      fontFamily: 'Roboto',
      textTheme: const TextTheme(
        headlineMedium: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 22,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
        titleMedium: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
        bodyLarge: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w500,
          fontFamily: 'monospace',
        ),
        bodyMedium: TextStyle(
          color: AppColors.textSecondary,
          fontSize: 14,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// Pure AMOLED #000000 True Black Theme for OLED Power Efficiency & Infinite Contrast
  static ThemeData get amoledDarkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.amoledBg,
      cardColor: AppColors.amoledCard,
      canvasColor: AppColors.amoledBg,
      colorScheme: const ColorScheme.dark(
        primary: AppColors.accentPrimary,
        secondary: AppColors.accentCorrect,
        surface: AppColors.amoledSurface,
        error: AppColors.accentError,
      ),
      fontFamily: 'Roboto',
      textTheme: const TextTheme(
        headlineMedium: TextStyle(
          color: Colors.white,
          fontSize: 22,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
        titleMedium: TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
        bodyLarge: TextStyle(
          color: Colors.white,
          fontSize: 18,
          fontWeight: FontWeight.w500,
          fontFamily: 'monospace',
        ),
        bodyMedium: TextStyle(
          color: AppColors.textSecondary,
          fontSize: 14,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.amoledBg,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: Colors.white,
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// WCAG 2.1 relative luminance calculation
  static double _channelLuminance(double v) {
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) * ((v + 0.055) / 1.055);
  }

  static double _relativeLuminance(Color c) {
    final r = _channelLuminance(c.r);
    final g = _channelLuminance(c.g);
    final b = _channelLuminance(c.b);
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  /// Calculates the WCAG contrast ratio between two colors. (Range: 1.0 to 21.0)
  static double calculateContrastRatio(Color foreground, Color background) {
    final l1 = _relativeLuminance(foreground);
    final l2 = _relativeLuminance(background);
    final brightest = l1 > l2 ? l1 : l2;
    final darkest = l1 > l2 ? l2 : l1;
    return (brightest + 0.05) / (darkest + 0.05);
  }
}
