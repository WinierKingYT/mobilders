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

  /// Current dynamic frame rate target adapting to battery levels (Stage 34)
  static FrameRateTarget get currentFrameRate => BatteryPowerOptimizer().targetFrameRate;

  /// Whether high-intensity particle animations are allowed under current battery state
  static bool get areParticlesEnabled => BatteryPowerOptimizer().enableParticleEffects;

  /// Whether device is in battery saver mode (battery <= 15%)
  static bool get isLowPowerMode => BatteryPowerOptimizer().isLowPowerMode;
}

/// Dynamic refresh rate targets for Samsung Galaxy S22 LTPO display (Stage 34)
enum FrameRateTarget {
  highRefresh120Hz(120, Duration(microseconds: 8333)),
  standard60Hz(60, Duration(microseconds: 16666)),
  powerSaver30Hz(30, Duration(microseconds: 33333));

  final int targetFps;
  final Duration frameBudget;
  const FrameRateTarget(this.targetFps, this.frameBudget);
}

/// Manages dynamic frame rate scaling (120Hz -> 60Hz) and visual throttling on low battery
class BatteryPowerOptimizer with ChangeNotifier {
  static final BatteryPowerOptimizer _instance = BatteryPowerOptimizer._internal();
  factory BatteryPowerOptimizer() => _instance;
  BatteryPowerOptimizer._internal();

  bool _isLowPowerMode = false;
  int _batteryLevelPercent = 100;
  FrameRateTarget _targetFrameRate = FrameRateTarget.highRefresh120Hz;
  bool _enableParticleEffects = true;
  bool _enableHeavyCanvasAnimations = true;

  bool get isLowPowerMode => _isLowPowerMode;
  int get batteryLevelPercent => _batteryLevelPercent;
  FrameRateTarget get targetFrameRate => _targetFrameRate;
  bool get enableParticleEffects => _enableParticleEffects;
  bool get enableHeavyCanvasAnimations => _enableHeavyCanvasAnimations;

  /// Updates current battery state and dynamically throttles frame rates & visuals.
  /// When battery drops to 15% or below (or manual power saver is active),
  /// high-refresh (120Hz LTPO) throttles to standard 60Hz or 30Hz,
  /// and heavy particle effects are disabled to conserve energy.
  void updateBatteryState({
    required int batteryLevelPercent,
    bool? isPowerSaverActive,
  }) {
    _batteryLevelPercent = batteryLevelPercent.clamp(0, 100);
    final isSaver = isPowerSaverActive ?? (_batteryLevelPercent <= 15);
    _isLowPowerMode = isSaver;

    if (_isLowPowerMode) {
      if (_batteryLevelPercent <= 5) {
        _targetFrameRate = FrameRateTarget.powerSaver30Hz;
      } else {
        _targetFrameRate = FrameRateTarget.standard60Hz;
      }
      _enableParticleEffects = false;
      _enableHeavyCanvasAnimations = false;
    } else {
      _targetFrameRate = FrameRateTarget.highRefresh120Hz;
      _enableParticleEffects = true;
      _enableHeavyCanvasAnimations = true;
    }
    notifyListeners();
  }

  bool get is120HzLtpoSyncEnabled => !_isLowPowerMode && _targetFrameRate == FrameRateTarget.highRefresh120Hz;

  Duration get currentFrameInterval => _targetFrameRate.frameBudget;

  void setTargetFrameRate(FrameRateTarget target) {
    _targetFrameRate = target;
    notifyListeners();
  }

  bool isFrameWithinBudget(Duration elapsed) {
    return elapsed <= _targetFrameRate.frameBudget;
  }

  void reset() {
    _isLowPowerMode = false;
    _batteryLevelPercent = 100;
    _targetFrameRate = FrameRateTarget.highRefresh120Hz;
    _enableParticleEffects = true;
    _enableHeavyCanvasAnimations = true;
    notifyListeners();
  }
}

/// Dynamic Picture & Vector Layer Caching for 120Hz LTPO flicker-free rendering (Stage 65)
class DynamicVectorLayerCache {
  static final Map<String, dynamic> _pictureLayerCache = {};

  static int get cachedLayerCount => _pictureLayerCache.length;

  static void cacheLayer(String key, dynamic layer) {
    _pictureLayerCache[key] = layer;
  }

  static dynamic getLayer(String key) => _pictureLayerCache[key];

  static bool hasLayer(String key) => _pictureLayerCache.containsKey(key);

  static void clear() {
    _pictureLayerCache.clear();
  }
}
