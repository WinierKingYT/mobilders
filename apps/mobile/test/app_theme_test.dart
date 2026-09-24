import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/core/app_theme.dart';

void main() {
  group('AppTheme & AMOLED Dark Mode Tests', () {
    test('Standard darkTheme uses slate 900 background', () {
      final theme = AppTheme.darkTheme;
      expect(theme.brightness, Brightness.dark);
      expect(theme.scaffoldBackgroundColor, AppColors.bgPrimary);
      expect(theme.cardColor, AppColors.bgSurface);
    });

    test('AMOLED darkTheme uses pure #000000 black background for 0W OLED battery efficiency', () {
      final theme = AppTheme.amoledDarkTheme;
      expect(theme.brightness, Brightness.dark);
      expect(theme.scaffoldBackgroundColor, const Color(0xFF000000));
      expect(theme.canvasColor, const Color(0xFF000000));
      expect(theme.cardColor, AppColors.amoledCard);
    });

    test('MathTypography dyscalculiaMath enforces 1.2 letter spacing', () {
      expect(MathTypography.dyscalculiaMath.letterSpacing, 1.2);
      expect(MathTypography.dyscalculiaMath.fontFamily, 'monospace');
    });

    test('MathTypography.toPrettyMath converts ASCII shortcuts to math symbols', () {
      final pretty = MathTypography.toPrettyMath('x^2 +- sqrt(4) * 2 / 1');
      expect(pretty, 'x² ± √(4) × 2 ÷ 1');
    });

    test('WCAG contrast ratio calculation verifies >= 7:1 AAA contrast on AMOLED black', () {
      // Pure White (#FFFFFF) on Pure Black (#000000) -> 21:1
      final whiteRatio = AppTheme.calculateContrastRatio(Colors.white, const Color(0xFF000000));
      expect(whiteRatio, greaterThanOrEqualTo(20.0));

      // App text primary on AMOLED background -> far exceeds WCAG AAA 7:1
      final textRatio = AppTheme.calculateContrastRatio(AppColors.textPrimary, AppColors.amoledBg);
      expect(textRatio, greaterThanOrEqualTo(7.0));

      // Accent Cyan glow on AMOLED background -> exceeds 7:1
      final cyanRatio = AppTheme.calculateContrastRatio(const Color(0xFF38BDF8), AppColors.amoledBg);
      expect(cyanRatio, greaterThanOrEqualTo(7.0));

      // Identical colors have 1:1 contrast
      final sameRatio = AppTheme.calculateContrastRatio(Colors.black, Colors.black);
      expect(sameRatio, closeTo(1.0, 0.01));
    });
  });
}
