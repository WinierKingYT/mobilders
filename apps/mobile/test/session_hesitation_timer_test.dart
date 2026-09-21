import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';

void main() {
  group('SessionViewModel Hesitation Timer & Contextual Whisper Tests', () {
    late SessionViewModel viewModel;

    setUp(() {
      viewModel = SessionViewModel(
        apiService: EngineApiService(),
        sessionId: 'sess_test_hesitation',
        targetEquation: '2*(x + 3) = 14',
      );
    });

    tearDown(() {
      viewModel.dispose();
    });

    test('Initial hesitation whisper is null', () {
      expect(viewModel.hesitationWhisper, isNull);
    });

    test('generateContextualWhisper returns formula-specific hints', () {
      // Parenthesis
      expect(
        SessionViewModel.generateContextualWhisper('2*(x + 3) = 10'),
        contains('parantezin'),
      );

      // Quadratic
      expect(
        SessionViewModel.generateContextualWhisper('x^2 + 6*x - 2 = 0'),
        contains('tüm terimleri eşitliğin bir tarafına'),
      );
      expect(
        SessionViewModel.generateContextualWhisper('x² - 9 = 0'),
        contains('tüm terimleri eşitliğin bir tarafına'),
      );

      // Fraction
      expect(
        SessionViewModel.generateContextualWhisper('x/3 + 1 = 5'),
        contains('paydaları eşitlemek'),
      );

      // Linear with =
      expect(
        SessionViewModel.generateContextualWhisper('2*x + 5 = 15'),
        contains("x'in yanındaki sabit sayıyı"),
      );

      // General fallback
      expect(
        SessionViewModel.generateContextualWhisper('3*x'),
        contains('Küçük bir ilk adımla'),
      );
    });

    test('startHesitationTimer fires whisper after configured duration', () async {
      viewModel.startHesitationTimer(duration: const Duration(milliseconds: 50));
      expect(viewModel.hesitationWhisper, isNull);

      await Future.delayed(const Duration(milliseconds: 75));
      expect(viewModel.hesitationWhisper, isNotNull);
      expect(viewModel.hesitationWhisper, contains('parantezin'));
    });

    test('resetHesitationTimer clears active whisper and restarts timer', () async {
      viewModel.startHesitationTimer(duration: const Duration(milliseconds: 50));
      await Future.delayed(const Duration(milliseconds: 75));
      expect(viewModel.hesitationWhisper, isNotNull);

      // Reset timer
      viewModel.resetHesitationTimer(duration: const Duration(milliseconds: 100));
      expect(viewModel.hesitationWhisper, isNull);

      await Future.delayed(const Duration(milliseconds: 120));
      expect(viewModel.hesitationWhisper, isNotNull);
    });

    test('dismissHesitationWhisper clears whisper and cancels timer', () async {
      viewModel.startHesitationTimer(duration: const Duration(milliseconds: 50));
      await Future.delayed(const Duration(milliseconds: 75));
      expect(viewModel.hesitationWhisper, isNotNull);

      viewModel.dismissHesitationWhisper();
      expect(viewModel.hesitationWhisper, isNull);

      // Verify timer does not fire again
      await Future.delayed(const Duration(milliseconds: 75));
      expect(viewModel.hesitationWhisper, isNull);
    });
  });
}
