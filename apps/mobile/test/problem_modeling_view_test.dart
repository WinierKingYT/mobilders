import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/modeling/problem_modeling_view.dart';
import 'package:personal_learning_engine/ui/features/modeling/widgets/motion_diagram_widget.dart';
import 'package:personal_learning_engine/ui/features/modeling/widgets/mixture_vessel_widget.dart';

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
}
