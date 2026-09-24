import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/modeling/problem_modeling_view.dart';
import 'package:personal_learning_engine/ui/features/modeling/widgets/motion_diagram_widget.dart';
import 'package:personal_learning_engine/ui/features/modeling/widgets/mixture_vessel_widget.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  testWidgets('ProblemModelingView renders story, initial stage, and advances through 3 stages', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(
          problemId: 'PROB_AGE_01',
          category: 'Yaş Problemleri',
          title: 'Babanın ve Oğlunun Yaşları',
          storyText: 'Bir babanın bugünkü yaşı oğlunun yaşının 3 katıdır. 5 yıl sonra toplam 50.',
          targetUnknown: 'Oğlun yaşı',
          schematicType: 'NONE',
        ),
      ),
    );

    // Initial check
    expect(find.text('Babanın ve Oğlunun Yaşları'), findsOneWidget);
    expect(find.text('Aşama 1: Bilinmeyeni Tanımla'), findsOneWidget);
    expect(find.text('Hangi büyüklüğe "x" demeliyiz?'), findsOneWidget);

    // Stage 1 -> Input 'x'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'x = oğlun yaşı');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pump();

    // Now in Stage 2
    expect(find.text('Aşama 2: Eşitliği Kur'), findsOneWidget);

    // Buggy rule test: input 'x + 5 = 2y'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'x + 5 = 2y');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pump();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-01'), findsOneWidget);

    // Valid equation: input '(x + 5) + (3*x + 5) = 50'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '(x + 5) + (3*x + 5) = 50');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pump();

    // Now in Stage 3
    expect(find.text('Aşama 3: Çöz ve Doğrula'), findsOneWidget);

    // Real-world domain check: negative root '-5'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'x = -5');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pump();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-10'), findsOneWidget);

    // Correct root: '10'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '10');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pump();

    expect(find.text('Modelleme Başarıyla Tamamlandı!'), findsOneWidget);
  });

  testWidgets('ProblemModelingView renders MotionDiagramWidget when MOTION_TIMELINE requested', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(
          schematicType: 'MOTION_TIMELINE',
        ),
      ),
    );

    expect(find.byType(MotionDiagramWidget), findsOneWidget);
    expect(find.text('Karşıt Yönlü Hareket Şeması'), findsOneWidget);
    expect(find.text('Karşılaşma'), findsOneWidget);
  });

  testWidgets('ProblemModelingView renders MixtureVesselWidget when MIXTURE_VESSEL requested', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(
          schematicType: 'MIXTURE_VESSEL',
        ),
      ),
    );

    expect(find.byType(MixtureVesselWidget), findsOneWidget);
    expect(find.text('Karışım ve Kap Denge Şeması (Tuz)'), findsOneWidget);
    expect(find.text('1. Kap'), findsOneWidget);
    expect(find.text('2. Kap'), findsOneWidget);
    expect(find.text('Karışım'), findsOneWidget);
  });

  testWidgets('ProblemModelingView preset selector chips switch problems and schematics', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(),
      ),
    );

    // Initially on Yaş Problemleri (index 0)
    expect(find.text('Babanın ve Oğlunun Yaşları'), findsOneWidget);
    expect(find.byType(MotionDiagramWidget), findsNothing);

    // Switch to Hareket Problemleri via chip
    await tester.tap(find.byKey(const Key('preset_chip_PROB_MOTION_01')));
    await tester.pumpAndSettle();

    expect(find.text('Karşıt Yönlü İki Aracın Karşılaşması'), findsOneWidget);
    expect(find.byType(MotionDiagramWidget), findsOneWidget);

    // Switch to Karışım Problemleri via chip
    await tester.tap(find.byKey(const Key('preset_chip_PROB_MIXTURE_01')));
    await tester.pumpAndSettle();

    expect(find.text('Tuzlu Su Karışımlarının Birleşimi'), findsOneWidget);
    expect(find.byType(MixtureVesselWidget), findsOneWidget);
  });

  testWidgets('ProblemModelingView detects BUG-PROB-06 (Work time linear addition)', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(),
      ),
    );

    // Switch to İşçi Problemleri
    await tester.tap(find.byKey(const Key('preset_chip_PROB_WORK_01')));
    await tester.pumpAndSettle();

    // Stage 1: Variable 't'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 't = süre');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 2: Buggy input '6 + 12 = 18'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '6 + 12 = 18');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-06'), findsOneWidget);
  });

  testWidgets('ProblemModelingView detects BUG-PROB-04 (Percentage reversal fallacy)', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(),
      ),
    );

    // Switch to Yüzde Problemleri
    await tester.tap(find.byKey(const Key('preset_chip_PROB_PERCENT_01')));
    await tester.pumpAndSettle();

    // Stage 1: Variable 'k'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'k = net kar');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 2: Buggy input '1.20*0.80 = 1'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '1.20*0.80 = 1');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-04'), findsOneWidget);
  });

  testWidgets('ProblemModelingView detects BUG-PROB-07 (Relative velocity sign inversion)', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(),
      ),
    );

    // Switch to Hareket Problemleri
    await tester.tap(find.byKey(const Key('preset_chip_PROB_MOTION_01')));
    await tester.pumpAndSettle();

    // Stage 1: Variable 't'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 't = karşılaşma süresi');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 2: Buggy input '(60 - 40) * t = 400'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '(60 - 40) * t = 400');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-07'), findsOneWidget);
  });

  testWidgets('ProblemModelingView displays live API badge and consumes API responses', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final mockApi = _MockModelingEngineApiService(
      onSubmit: ({
        required String sessionId,
        required String problemId,
        required String stage,
        required String studentInput,
        String? variableName,
        String? studentId,
      }) async {
        if (stage == 'STAGE_1_VARIABLE') {
          return {
            'problem_id': problemId,
            'stage': stage,
            'is_valid': true,
            'stage_completed': true,
            'next_stage': 'STAGE_2_EQUATION',
            'socratic_feedback': 'API Doğrulandı: Değişken doğru tanımlandı.',
          };
        } else if (stage == 'STAGE_2_EQUATION') {
          return {
            'problem_id': problemId,
            'stage': stage,
            'is_valid': false,
            'stage_completed': false,
            'detected_bug': {'bug_id': 'BUG-PROB-02'},
            'socratic_feedback': 'API Sokratik: Hız ile zaman ters orantılıdır.',
          };
        }
        return {'is_valid': false};
      },
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ProblemModelingView(apiService: mockApi),
      ),
    );

    // Verify online badge
    expect(find.text('Canlı API'), findsOneWidget);

    // Stage 1 with mock API
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'x');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('API Doğrulandı: Değişken doğru tanımlandı.'), findsOneWidget);
    expect(find.text('Aşama 2: Eşitliği Kur'), findsOneWidget);

    // Stage 2 with mock API returning bug
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'v1/v2 = t1/t2');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-02'), findsOneWidget);
    expect(find.text('API Sokratik: Hız ile zaman ters orantılıdır.'), findsOneWidget);
  });

  testWidgets('ProblemModelingView falls back to offline local evaluation when API throws', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final mockApi = _MockModelingEngineApiService(
      onSubmit: ({
        required String sessionId,
        required String problemId,
        required String stage,
        required String studentInput,
        String? variableName,
        String? studentId,
      }) async {
        throw Exception("Network connection timeout");
      },
    );

    await tester.pumpWidget(
      MaterialApp(
        home: ProblemModelingView(apiService: mockApi),
      ),
    );

    // Stage 1 -> fallback to local
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'x = oğlun yaşı');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 1 passed via local fallback
    expect(find.text('Aşama 2: Eşitliği Kur'), findsOneWidget);
  });

  testWidgets('ProblemModelingView completes full flow for Optimization problem preset', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(2400, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(),
      ),
    );

    // Ensure visible & Switch to Optimizasyon
    await tester.ensureVisible(find.byKey(const Key('preset_chip_PROB_OPTIMIZATION_01')));
    await tester.tap(find.byKey(const Key('preset_chip_PROB_OPTIMIZATION_01')));
    await tester.pumpAndSettle();

    expect(find.text('Bahçe Alanını Maksimum Yapma'), findsOneWidget);
    expect(find.text('Çevrimdışı'), findsOneWidget);

    // Stage 1: x
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'x = kenar');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 2: x * (30 - x) = 225
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 'x * (30 - x) = 225');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 3: 15
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '15');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Modelleme Başarıyla Tamamlandı!'), findsOneWidget);
  });

  test('ProblemModelingPhysics clamps time, velocity, volume, ratio, and percentage strictly', () {
    expect(ProblemModelingPhysics.clampTime(-5.0), 0.0);
    expect(ProblemModelingPhysics.clampTime(12.5), 12.5);
    expect(ProblemModelingPhysics.clampTime(double.nan), 0.0);

    expect(ProblemModelingPhysics.clampVelocity(-10.0), 0.001);
    expect(ProblemModelingPhysics.clampVelocity(0.0), 0.001);
    expect(ProblemModelingPhysics.clampVelocity(65.0), 65.0);

    expect(ProblemModelingPhysics.clampVolume(-2.0), 0.001);
    expect(ProblemModelingPhysics.clampVolume(0.0), 0.001);
    expect(ProblemModelingPhysics.clampVolume(40.0), 40.0);

    expect(ProblemModelingPhysics.clampRatio(-0.2), 0.0);
    expect(ProblemModelingPhysics.clampRatio(0.45), 0.45);
    expect(ProblemModelingPhysics.clampRatio(1.5), 1.0);

    expect(ProblemModelingPhysics.clampPercentage(-10.0), 0.0);
    expect(ProblemModelingPhysics.clampPercentage(25.0), 25.0);
    expect(ProblemModelingPhysics.clampPercentage(150.0), 100.0);

    expect(MotionDiagramWidget.clampDistance(-100.0), 0.0);
    expect(MotionDiagramWidget.clampVelocity(0.0), 0.001);
    expect(MotionDiagramWidget.clampTime(-2.0), 0.0);

    expect(MixtureVesselWidget.clampVolume(0.0), 0.001);
    expect(MixtureVesselWidget.clampPercentage(-5.0), 0.0);
    expect(MixtureVesselWidget.clampRatio(2.0), 1.0);
  });

  testWidgets('ProblemModelingView detects BUG-PROB-DIV-ZERO when division by zero entered in equation', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(),
      ),
    );

    // Switch to İşçi Problemleri
    await tester.tap(find.byKey(const Key('preset_chip_PROB_WORK_01')));
    await tester.pumpAndSettle();

    // Stage 1: Variable 't'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 't = süre');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 2: Input with division by zero '1/0 + 1/12 = 1/t'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '1/0 + 1/12 = 1/t');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-DIV-ZERO'), findsOneWidget);
    expect(find.text('Çalışma süresi sıfır veya negatif olamaz (sıfıra bölme tanımsızdır).'), findsOneWidget);
  });

  testWidgets('ProblemModelingView detects BUG-PROB-DIV-ZERO when work time is zero in solve stage', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: ProblemModelingView(),
      ),
    );

    // Switch to İşçi Problemleri
    await tester.tap(find.byKey(const Key('preset_chip_PROB_WORK_01')));
    await tester.pumpAndSettle();

    // Stage 1: Variable 't'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 't = süre');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    // Stage 2: Valid equation '1/6 + 1/12 = 1/t'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '1/6 + 1/12 = 1/t');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Aşama 3: Çöz ve Doğrula'), findsOneWidget);

    // Stage 3: Zero work time 't = 0'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), 't = 0');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Bilişsel Yanılgı: BUG-PROB-DIV-ZERO'), findsOneWidget);
    expect(find.text('Çalışma süresi sıfır veya negatif olamaz (sıfıra bölme tanımsızdır).'), findsOneWidget);

    // Stage 3: Correct answer '4'
    await tester.enterText(find.byKey(const Key('modeling_input_field')), '4');
    await tester.tap(find.byKey(const Key('modeling_submit_button')));
    await tester.pumpAndSettle();

    expect(find.text('Modelleme Başarıyla Tamamlandı!'), findsOneWidget);
  });
}

class _MockModelingEngineApiService extends Fake implements EngineApiService {
  final Future<Map<String, dynamic>> Function({
    required String sessionId,
    required String problemId,
    required String stage,
    required String studentInput,
    String? variableName,
    String? studentId,
  }) onSubmit;

  _MockModelingEngineApiService({required this.onSubmit});

  @override
  Future<Map<String, dynamic>> submitModelingScaffoldStep({
    required String sessionId,
    required String problemId,
    required String stage,
    required String studentInput,
    String? variableName,
    String? studentId,
  }) async {
    return onSubmit(
      sessionId: sessionId,
      problemId: problemId,
      stage: stage,
      studentInput: studentInput,
      variableName: variableName,
      studentId: studentId,
    );
  }
}

