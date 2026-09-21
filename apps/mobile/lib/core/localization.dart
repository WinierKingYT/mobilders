
/// International Curriculum Standard Selection.
enum CurriculumType {
  meb,
  ibAA,
  ibAI,
  ccss,
  apPrecalc,
}

extension CurriculumExtension on CurriculumType {
  String get code {
    switch (this) {
      case CurriculumType.meb:
        return 'MEB';
      case CurriculumType.ibAA:
        return 'IB_AA';
      case CurriculumType.ibAI:
        return 'IB_AI';
      case CurriculumType.ccss:
        return 'CCSS';
      case CurriculumType.apPrecalc:
        return 'AP_PRECALC';
    }
  }

  String get displayName {
    switch (this) {
      case CurriculumType.meb:
        return 'Türkiye MEB (Kazanımlar)';
      case CurriculumType.ibAA:
        return 'IB DP Math (Analysis & Approaches)';
      case CurriculumType.ibAI:
        return 'IB DP Math (Applications & Interpretation)';
      case CurriculumType.ccss:
        return 'US Common Core (CCSS High School)';
      case CurriculumType.apPrecalc:
        return 'College Board AP Precalculus';
    }
  }
}

/// Lightweight Multi-Language Localization Engine.
class AppLocalization {
  static String currentLanguage = 'tr';
  static CurriculumType currentCurriculum = CurriculumType.meb;

  static final Map<String, Map<String, String>> _localizedValues = {
    'tr': {
      'app_title': 'Kişisel Öğrenme Motoru',
      'mode_inking': 'El Yazısı Kanvası',
      'mode_touchpad': 'Matematik Touchpad',
      'mode_keyboard': 'Cebirsel Klavye',
      'submit_step': 'Adımı Doğrula',
      'undo': 'Geri Al',
      'clear': 'Temizle',
      'recognized_preview': 'Tanınan İfade',
      'transfer_step': 'Adımı Aktar',
      'socratic_tutor': 'Sokratik Yapay Zeka Rehber',
      'zpd_frontier': 'Yakınsak Gelişim Alanı (ZPD)',
      'curriculum_standard': 'Müfredat Kazanımı',
      'voice_guidance': 'Sesli Sokratik Rehber',
      'voice_speak_now': 'Şimdi konuşabilirsiniz...',
      'classroom_analytics': 'Sıfır-PII Sınıf Analitiği',
    },
    'en': {
      'app_title': 'Personal Learning Engine',
      'mode_inking': 'Freehand Inking Canvas',
      'mode_touchpad': 'Math Touchpad',
      'mode_keyboard': 'Algebraic Keyboard',
      'submit_step': 'Verify Step',
      'undo': 'Undo',
      'clear': 'Clear',
      'recognized_preview': 'Recognized Expression',
      'transfer_step': 'Transfer Step',
      'socratic_tutor': 'Socratic AI Tutor',
      'zpd_frontier': 'Zone of Proximal Development (ZPD)',
      'curriculum_standard': 'Curriculum Standard',
      'voice_guidance': 'Voice Socratic Guidance',
      'voice_speak_now': 'Listening to your voice...',
      'classroom_analytics': 'Zero-PII Classroom Analytics',
    },
  };

  static String text(String key) {
    final langMap = _localizedValues[currentLanguage] ?? _localizedValues['tr']!;
    return langMap[key] ?? key;
  }

  static void setLanguage(String lang) {
    if (_localizedValues.containsKey(lang)) {
      currentLanguage = lang;
    }
  }

  static void setCurriculum(CurriculumType type) {
    currentCurriculum = type;
  }
}
