import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../domain/models/solution_step.dart';
import '../../domain/models/diagnostic_item.dart';
import '../../domain/models/misconception_profile_model.dart';
import '../../domain/models/twin_question_model.dart';

class EngineApiService {
  final String baseUrl;
  final http.Client _client;

  EngineApiService({
    String? baseUrl,
    http.Client? client,
  })  : baseUrl = (baseUrl ?? _defaultBaseUrl()).replaceAll(RegExp(r'/+$'), ''),
        _client = client ?? http.Client();

  static String _defaultBaseUrl() {
    // 127.0.0.1 routes correctly via adb reverse on Android and localhost on desktop/web
    return 'http://127.0.0.1:8000';
  }

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
    final uri = Uri.parse('$baseUrl/api/v1/session/step/verify');
    final payload = {
      'session_id': sessionId,
      'node_id': nodeId,
      'step_number': stepNumber,
      'user_expression': userExpression,
      'target_equation': targetEquation,
      if (previousStep != null) 'previous_step': previousStep,
      if (elapsedMs != null) 'elapsed_ms': elapsedMs,
      if (currentPl != null) 'current_p_l': currentPl,
      if (clientMsgId != null) 'client_msg_id': clientMsgId,
      if (clientTimestamp != null) 'client_timestamp': clientTimestamp.toIso8601String(),
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return SolutionStep.fromJson(
        json,
        stepNumber: stepNumber,
        userExpression: userExpression,
        elapsedMs: elapsedMs ?? 0,
      );
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> replayOfflineBatch({
    required String sessionId,
    required List<Map<String, dynamic>> events,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/session/replay-queue');
    final payload = {
      'session_id': sessionId,
      'events': events,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  /// Requests multi-turn Socratic tutoring guidance from the core engine.
  Future<Map<String, dynamic>> requestSocraticGuidance({
    required String userInput,
    required String targetEquation,
    String? previousStep,
    List<double> solutionRoots = const [],
    Map<String, dynamic>? diagnosticBug,
    String affectiveState = 'FLOW',
    int scaffoldingLevel = 1,
    String language = 'tr',
    List<Map<String, String>> conversationHistory = const [],
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/socratic/respond');
    final payload = {
      'user_input': userInput,
      'target_equation': targetEquation,
      if (previousStep != null) 'previous_step': previousStep,
      'solution_roots': solutionRoots,
      if (diagnosticBug != null) 'diagnostic_bug': diagnosticBug,
      'affective_state': affectiveState,
      'scaffolding_level': scaffoldingLevel,
      'language': language,
      'conversation_history': conversationHistory,
    };

    try {
      final response = await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      ).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw HttpException('Server returned ${response.statusCode}: ${response.body}', uri: uri);
      }
    } catch (e) {
      // Graceful fallback for offline mode or network errors
      return {
        'final_output': _fallbackSocraticResponse(userInput, diagnosticBug, language),
        'socratic_ratio': 2.0,
        'layer1_pedagogical_intent': 'LOCAL_OFFLINE_FALLBACK',
      };
    }
  }

  static String _fallbackSocraticResponse(String input, Map<String, dynamic>? bug, String lang) {
    final isEn = lang.toLowerCase() == 'en';
    final remediation = bug?['remediation_directive'] as String?;
    if (remediation != null && remediation.trim().isNotEmpty) {
      return remediation;
    }

    final bugId = bug?['bug_id'] as String?;
    if (bugId == 'BUG-QUAD-03') {
      return isEn
          ? 'Can you visualize the geometric area model when squaring a binomial (x + a)? Where should the two middle rectangular terms of area ax go?'
          : 'İki terimin toplamının karesini alırken alan modelini hatırla. İki adet ax alanlı dikdörtgen terimini nereye yerleştirmeliyiz?';
    } else if (bugId == 'BUG-QUAD-02') {
      return isEn
          ? 'Could there also be a negative twin root whose square equals this target number?'
          : 'Karesi bu hedef sayıyı veren negatif bir ikiz kök de var olabilir mi?';
    } else if (bugId == 'BUG-QUAD-01') {
      return isEn
          ? 'Can the zero-product property apply when the other side of the equation is non-zero?'
          : 'Eşitliğin sağ tarafı sıfırdan farklı bir sayı iken sıfır-çarpım kuralı geçerli olabilir mi?';
    }
    return isEn
        ? 'What algebraic operation should we apply to both sides now to maintain balance?'
        : 'Bu aşamada eşitliği korumak için her iki tarafa hangi işlemi uygulamalıyız?';
  }

  Future<DiagnosticItem?> getNextCatItem({
    required String sessionId,
    required double currentTheta,
    required List<String> administeredItemIds,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/diagnostic/next-item');
    final payload = {
      'session_id': sessionId,
      'current_theta': currentTheta,
      'administered_item_ids': administeredItemIds,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      if (response.body.isEmpty || response.body.trim() == 'null') return null;
      final dynamic decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic> && decoded.containsKey('item_id')) {
        return DiagnosticItem.fromJson(decoded);
      }
      return null;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<DiagnosticSubmitResult> submitCatResponse({
    required String sessionId,
    required String itemId,
    required bool isCorrect,
    required List<List<dynamic>> administeredHistory,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/diagnostic/submit');
    final payload = {
      'session_id': sessionId,
      'item_id': itemId,
      'is_correct': isCorrect,
      'administered_history': administeredHistory,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return DiagnosticSubmitResult.fromJson(json);
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> startDailySession({
    String? userId,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/session/start-daily');
    final payload = {
      if (userId != null) 'user_id': userId,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> concludeDailySession({
    String? sessionId,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/session/conclude');
    final payload = {
      if (sessionId != null) 'session_id': sessionId,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> startCatSession({
    String? sessionId,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/cat/start');
    final payload = {
      if (sessionId != null) 'session_id': sessionId,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> scanAndDiagnoseNotebook({
    String? imageBase64,
    String? rawTextOverride,
    String? targetProblem,
    String? studentId,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/scan/diagnose');
    final payload = {
      if (imageBase64 != null) 'image_base64': imageBase64,
      if (rawTextOverride != null) 'raw_text_override': rawTextOverride,
      if (targetProblem != null) 'target_problem': targetProblem,
      'student_id': studentId ?? 'STU-SCAN-01',
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchModelingProblems() async {
    final uri = Uri.parse('$baseUrl/api/v1/modeling/problems');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> fetchModelingProblem(String problemId) async {
    final uri = Uri.parse('$baseUrl/api/v1/modeling/problem/$problemId');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitModelingScaffoldStep({
    required String sessionId,
    required String problemId,
    required String stage,
    required String studentInput,
    String? variableName,
    String? studentId,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/modeling/scaffold/step');
    final payload = {
      'session_id': sessionId,
      'problem_id': problemId,
      'stage': stage,
      'student_input': studentInput,
      'variable_name': variableName ?? 'x',
      'student_id': studentId ?? 'STU-MODEL-01',
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> solveAnalyticGeometry({
    required String task,
    required Map<String, dynamic> params,
    String? studentId,
    String? problemStatement,
    String? studentStep,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/geometry/analytic/solve');
    final payload = {
      'task': task,
      'params': params,
      if (studentId != null) 'student_id': studentId,
      if (problemStatement != null) 'problem_statement': problemStatement,
      if (studentStep != null) 'student_step': studentStep,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> solveSyntheticGeometry({
    required String task,
    required Map<String, dynamic> params,
    String? studentId,
    String? problemStatement,
    String? studentStep,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/geometry/synthetic/solve');
    final payload = {
      'task': task,
      'params': params,
      if (studentId != null) 'student_id': studentId,
      if (problemStatement != null) 'problem_statement': problemStatement,
      if (studentStep != null) 'student_step': studentStep,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchVaultMistakes(
    String userId, {
    String? status,
  }) async {
    final query = status != null ? '?status=$status' : '';
    final uri = Uri.parse('$baseUrl/api/v1/vault/list/$userId$query');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchDueVaultMistakes(String userId) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/due/$userId');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> fetchVaultAnalytics(String userId) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/analytics/$userId');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<MisconceptionProfileResponse> fetchMisconceptionProfile(String userId) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/misconception-profile/$userId');
    try {
      final response = await _client.get(uri).timeout(const Duration(seconds: 4));
      if (response.statusCode == 200) {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        return MisconceptionProfileResponse.fromJson(json);
      }
    } catch (_) {
      // Graceful offline fallback
    }

    return MisconceptionProfileResponse(
      userId: userId,
      totalRecordedMistakes: 0,
      totalCured: 0,
      overallCureRate: 0.0,
      topRecurringTraps: const [],
      categories: const [
        MisconceptionCategory(
          categoryId: 'KUADRATIK_DENKLEMLER',
          categoryTitle: 'Kuadratik Denklemler',
          totalMistakes: 0,
          activeMistakes: 0,
          curedMistakes: 0,
          nodes: [],
        ),
        MisconceptionCategory(
          categoryId: 'ISARET_VE_DAGILMA',
          categoryTitle: 'İşaret ve Parantez Dağılımı',
          totalMistakes: 0,
          activeMistakes: 0,
          curedMistakes: 0,
          nodes: [],
        ),
        MisconceptionCategory(
          categoryId: 'PARABOL_VE_POLINOM',
          categoryTitle: 'Parabol ve Polinomlar',
          totalMistakes: 0,
          activeMistakes: 0,
          curedMistakes: 0,
          nodes: [],
        ),
        MisconceptionCategory(
          categoryId: 'TRIGONOMETRI_VE_LOGARITMA',
          categoryTitle: 'Trigonometri ve Logaritma',
          totalMistakes: 0,
          activeMistakes: 0,
          curedMistakes: 0,
          nodes: [],
        ),
        MisconceptionCategory(
          categoryId: 'ANALIZ_TUREV_INTEGRAL',
          categoryTitle: 'Analiz (Türev & İntegral)',
          totalMistakes: 0,
          activeMistakes: 0,
          curedMistakes: 0,
          nodes: [],
        ),
      ],
    );
  }

  Future<TwinQuestionModel> generateTwinQuestion({
    required String bugId,
    String? originalEquation,
    int difficultyLevel = 1,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/twin/generate');
    final payload = {
      'bug_id': bugId,
      if (originalEquation != null) 'original_equation': originalEquation,
      'difficulty_level': difficultyLevel,
    };

    try {
      final response = await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      ).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        return TwinQuestionModel.fromJson(json);
      }
    } catch (_) {
      // Graceful offline fallback
    }

    return _fallbackTwinQuestion(bugId, difficultyLevel);
  }

  static TwinQuestionModel _fallbackTwinQuestion(String bugId, int difficulty) {
    final b = bugId.toUpperCase();
    if (b == 'BUG-QUAD-01') {
      return const TwinQuestionModel(
        twinId: 'twin_offline_01',
        targetEquation: '(x - 3)(x + 2) = 6',
        canonicalRoots: [4.0, -3.0],
        targetedBugId: 'BUG-QUAD-01',
        targetedBugTitle: 'Sıfır-Çarpım Kuralı İhlali',
        pedagogicalFocus: 'Eşitliğin sağ tarafı sıfırdan farklıdır. Önce parantezleri açıp tüm terimleri bir tarafa toplamalısın.',
        hint: 'Önce sol tarafı aç: x² - x - 6 = 6. Sonra 6 çıkar: x² - x - 12 = 0.',
      );
    } else if (b == 'BUG-QUAD-02') {
      return const TwinQuestionModel(
        twinId: 'twin_offline_02',
        targetEquation: 'x² = 49',
        canonicalRoots: [7.0, -7.0],
        targetedBugId: 'BUG-QUAD-02',
        targetedBugTitle: 'Negatif İkiz Kök İhmali',
        pedagogicalFocus: 'Karesi pozitif bir sayı olan denklemlerde negatif kökü de (±√c) unutma.',
        hint: 'Karesi 49 olan sayılar: x = 7 ve x = -7.',
      );
    } else if (b == 'BUG-QUAD-03') {
      return const TwinQuestionModel(
        twinId: 'twin_offline_03',
        targetEquation: '(x - 4)² = 25',
        canonicalRoots: [9.0, -1.0],
        targetedBugId: 'BUG-QUAD-03',
        targetedBugTitle: 'Binom Karesi Açılım Hatası',
        pedagogicalFocus: '(x ± a)² açılımında ortadaki 2ax terimini unutma.',
        hint: '(x - 4)² = x² - 8x + 16.',
      );
    }
    return const TwinQuestionModel(
      twinId: 'twin_offline_generic',
      targetEquation: 'x² - 5x + 6 = 0',
      canonicalRoots: [3.0, 2.0],
      targetedBugId: 'GENERIC',
      targetedBugTitle: 'Kavramsal Pekiştirme',
      pedagogicalFocus: 'Temel cebirsel kuralları adım adım uygulayarak denklemi çöz.',
      hint: '(x - 3)(x - 2) = 0 şeklinde çarpanlara ayır.',
    );
  }

  Future<Map<String, dynamic>> recordVaultMistake({
    required String userId,
    required String nodeId,
    required String bugId,
    required String problemStatement,
    required String offendingStep,
    required String correctPrinciple,
    required String remediationDirective,
    double? timestamp,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/record');
    final payload = {
      'user_id': userId,
      'node_id': nodeId,
      'bug_id': bugId,
      'problem_statement': problemStatement,
      'offending_step': offendingStep,
      'correct_principle': correctPrinciple,
      'remediation_directive': remediationDirective,
      if (timestamp != null) 'timestamp': timestamp,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> startSelfCorrection(String mistakeId) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/start');
    final payload = {'mistake_id': mistakeId};

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitSelfCorrectionDiagnosis({
    required String mistakeId,
    required bool isIdentified,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/diagnose');
    final payload = {
      'mistake_id': mistakeId,
      'is_identified': isIdentified,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitSelfCorrectionExplanation({
    required String mistakeId,
    required bool isPrincipleCorrect,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/explain');
    final payload = {
      'mistake_id': mistakeId,
      'is_principle_correct': isPrincipleCorrect,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitSelfCorrectionResolve({
    required String mistakeId,
    required bool isCorrect,
    double? currentTime,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/resolve');
    final payload = {
      'mistake_id': mistakeId,
      'is_correct': isCorrect,
      if (currentTime != null) 'current_time': currentTime,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> spawnBossBattle({
    required String userId,
    double? currentTime,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/boss-battle/spawn');
    final payload = {
      'user_id': userId,
      if (currentTime != null) 'current_time': currentTime,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitBossBattleTurn({
    required String battleId,
    required bool isCleanSolve,
    double? currentTime,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/boss-battle/turn');
    final payload = {
      'battle_id': battleId,
      'is_clean_solve': isCleanSolve,
      if (currentTime != null) 'current_time': currentTime,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> generateDynamicExam({
    String section = 'TYT_MATEMATIK',
    int questionCount = 10,
    double targetTheta = 0.0,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/exam/generate');
    final payload = {
      'section': section,
      'question_count': questionCount,
      'target_theta': targetTheta,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> gradeDynamicExam({
    required Map<String, dynamic> exam,
    required Map<int, int> answers,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/exam/grade');
    // JSON keys for answers must be stringified in HTTP body
    final stringKeyAnswers = answers.map((k, v) => MapEntry(k.toString(), v));
    final payload = {
      'exam': exam,
      'answers': stringKeyAnswers,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> exportDynamicExam({
    required Map<String, dynamic> exam,
    String format = 'html',
    bool includeSolutions = true,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/exam/export');
    final payload = {
      'exam': exam,
      'format': format,
      'include_solutions': includeSolutions,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> generateTargetedTrapQuestion({
    required String bugId,
    int? seed,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/exam/question/targeted');
    final payload = {
      'bug_id': bugId,
      if (seed != null) 'seed': seed,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> verifyTrapQuestion(Map<String, dynamic> question) async {
    final uri = Uri.parse('$baseUrl/api/v1/exam/question/verify');
    final payload = {'question': question};

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> solveProbabilityOrCombinatorics({
    required String problemType,
    required Map<String, dynamic> params,
    String? studentId,
    String? problemStatement,
    String? studentStep,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/probability/solve');
    final payload = {
      'problem_type': problemType,
      'params': params,
      if (studentId != null) 'student_id': studentId,
      if (problemStatement != null) 'problem_statement': problemStatement,
      if (studentStep != null) 'student_step': studentStep,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> simulateMonteCarlo({
    required String experimentType,
    required Map<String, dynamic> params,
    int numTrials = 100000,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/probability/monte-carlo');
    final payload = {
      'experiment_type': experimentType,
      'params': params,
      'num_trials': numTrials,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> generateTruthTable({
    required List<String> variables,
    String expressionType = 'implies',
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/proof/truth-table');
    final payload = {
      'variables': variables,
      'expression_type': expressionType,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchProofCatalog() async {
    final uri = Uri.parse('$baseUrl/api/v1/proof/catalog');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> verifyProofStep({
    required String theoremId,
    required int stepNumber,
    required String studentStatement,
    required String selectedRule,
    String? studentId,
    String? problemStatement,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/proof/verify-step');
    final payload = {
      'theorem_id': theoremId,
      'step_number': stepNumber,
      'student_statement': studentStatement,
      'selected_rule': selectedRule,
      if (studentId != null) 'student_id': studentId,
      if (problemStatement != null) 'problem_statement': problemStatement,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> simulateInduction({
    String claimType = 'gauss',
    int startK = 1,
    int testRange = 10,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/proof/induction/simulate');
    final payload = {
      'claim_type': claimType,
      'start_k': startK,
      'test_range': testRange,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> fetchAtlasSummary() async {
    final uri = Uri.parse('$baseUrl/api/v1/atlas/summary');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> fetchAtlasPayload({
    List<String>? masteredIds,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/atlas/payload');
    final payload = {
      'mastered_ids': masteredIds ?? [],
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchAtlasBottlenecks({
    List<String>? masteredIds,
    int topK = 5,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/atlas/bottlenecks');
    final payload = {
      'mastered_ids': masteredIds ?? [],
      'top_k': topK,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<String>> fetchAtlasZpd({
    List<String>? masteredIds,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/atlas/zpd');
    final payload = {
      'mastered_ids': masteredIds ?? [],
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e.toString()).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> fetchAtlasProgress({
    List<String>? masteredIds,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/atlas/progress');
    final payload = {
      'mastered_ids': masteredIds ?? [],
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  void dispose() {
    _client.close();
  }
}
