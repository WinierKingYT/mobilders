import 'package:flutter/material.dart';
import '../../../../core/services/haptic_feedback_service.dart';

enum RootCanvasMode {
  numberLine,
  pieFraction,
  balanceScale,
}

/// Dokunmatik Sayı Doğrusu, Pasta Kesir ve Terazi Kanvası (NumberLineBalanceCanvas).
/// Bruner E-I-S (Enactive - Iconic - Symbolic) ilkelerine göre Seviye -3..-1 kök kavramları öğretir.
class NumberLineBalanceCanvas extends StatefulWidget {
  final RootCanvasMode initialMode;
  final double scaffoldOpacity;
  final ValueChanged<String>? onEquationChanged;
  final ValueChanged<String>? onDualCodingAction;

  const NumberLineBalanceCanvas({
    super.key,
    this.initialMode = RootCanvasMode.numberLine,
    this.scaffoldOpacity = 1.0,
    this.onEquationChanged,
    this.onDualCodingAction,
  });

  @override
  State<NumberLineBalanceCanvas> createState() => _NumberLineBalanceCanvasState();
}

class _NumberLineBalanceCanvasState extends State<NumberLineBalanceCanvas> {
  late RootCanvasMode _currentMode;

  // 1. Sayı Doğrusu Durumu
  int _currentPos = 0;

  // 2. Pasta Kesir Durumu
  int _fractionSlices = 4;
  int _shadedSlices = 1;

  // 3. Terazi Durumu
  int _leftWeight = 3;
  int _rightWeight = 11;
  final int _boxValue = 4; // 2x + 3 = 11 => 2x = 8 => x = 4
  String? _lastDualAction;

  @override
  void initState() {
    super.initState();
    _currentMode = widget.initialMode;
  }

  @override
  void didUpdateWidget(covariant NumberLineBalanceCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialMode != widget.initialMode) {
      _currentMode = widget.initialMode;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.amberAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Başlık ve Mod Seçici Sekmeler
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.toys, color: Colors.amberAccent, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'Kök Pedagoji Mikro-Kum Havuzu',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.amberAccent.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Text(
                  'Seviye -3..-1',
                  style: TextStyle(color: Colors.amberAccent, fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Sekme Butonları
          Row(
            children: [
              _buildTabButton('Sayı Doğrusu', RootCanvasMode.numberLine, Icons.linear_scale),
              const SizedBox(width: 8),
              _buildTabButton('Pasta Kesir', RootCanvasMode.pieFraction, Icons.pie_chart),
              const SizedBox(width: 8),
              _buildTabButton('Terazi', RootCanvasMode.balanceScale, Icons.balance),
            ],
          ),
          const SizedBox(height: 16),
          // Aktif Kanvas
          if (_currentMode == RootCanvasMode.numberLine)
            _buildNumberLineCanvas()
          else if (_currentMode == RootCanvasMode.pieFraction)
            _buildPieFractionCanvas()
          else
            _buildBalanceScaleCanvas(),
        ],
      ),
    );
  }

  Widget _buildTabButton(String label, RootCanvasMode mode, IconData icon) {
    final bool isActive = _currentMode == mode;
    return Expanded(
      child: InkWell(
        onTap: () => setState(() => _currentMode = mode),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isActive ? Colors.amberAccent : Colors.white10,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 14, color: isActive ? Colors.black : Colors.white70),
              const SizedBox(width: 4),
              Text(
                label,
                style: TextStyle(
                  color: isActive ? Colors.black : Colors.white70,
                  fontSize: 11,
                  fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ==========================================
  // 1. DOKUNMATİK SAYI DOĞRUSU
  // ==========================================
  Widget _buildNumberLineCanvas() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(8)),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Konum: $_currentPos', style: const TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 13)),
              Text(
                _currentPos < 0 ? 'Borç / Kayıp Alanı' : (_currentPos > 0 ? 'Alacak / Kazanç Alanı' : 'Sıfır Denge'),
                style: TextStyle(color: _currentPos < 0 ? Colors.redAccent : Colors.greenAccent, fontSize: 11),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        // Sayı doğrusu ekseni (-6'dan +6'ya)
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: List.generate(13, (index) {
              final val = index - 6;
              final isCurrent = val == _currentPos;
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: InkWell(
                  onTap: () => setState(() => _currentPos = val),
                  child: Container(
                    width: 34,
                    height: 48,
                    decoration: BoxDecoration(
                      color: isCurrent ? Colors.amberAccent : Colors.white10,
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: val == 0 ? Colors.cyanAccent : Colors.transparent),
                    ),
                    child: Center(
                      child: Text(
                        '$val',
                        style: TextStyle(
                          color: isCurrent ? Colors.black : Colors.white,
                          fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
        ),
        const SizedBox(height: 12),
        // Adım atma butonları
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton.icon(
              key: const Key('btn_step_left'),
              onPressed: _currentPos > -6
                  ? () => setState(() => _currentPos = (_currentPos - 1).clamp(-6, 6))
                  : null,
              icon: const Icon(Icons.arrow_back, size: 14),
              label: const Text('1 Sola Yürü (-1)', style: TextStyle(fontSize: 11)),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent.withValues(alpha: 0.3)),
            ),
            const SizedBox(width: 12),
            ElevatedButton.icon(
              key: const Key('btn_step_right'),
              onPressed: _currentPos < 6
                  ? () => setState(() => _currentPos = (_currentPos + 1).clamp(-6, 6))
                  : null,
              icon: const Icon(Icons.arrow_forward, size: 14),
              label: const Text('1 Sağa Yürü (+1)', style: TextStyle(fontSize: 11)),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent.withValues(alpha: 0.3)),
            ),
          ],
        ),
      ],
    );
  }

  // ==========================================
  // 2. PASTA KESİR MODELİ
  // ==========================================
  Widget _buildPieFractionCanvas() {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            Column(
              children: [
                const Text('Toplam Dilim (Payda)', style: TextStyle(color: Colors.white70, fontSize: 11)),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.remove_circle_outline, color: Colors.amberAccent, size: 18),
                      onPressed: _fractionSlices > 2
                          ? () => setState(() {
                                _fractionSlices--;
                                if (_shadedSlices > _fractionSlices) {
                                  _shadedSlices = _fractionSlices;
                                }
                              })
                          : null,
                    ),
                    Text('$_fractionSlices', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline, color: Colors.amberAccent, size: 18),
                      onPressed: _fractionSlices < 8 ? () => setState(() => _fractionSlices++) : null,
                    ),
                  ],
                ),
              ],
            ),
            Column(
              children: [
                const Text('Dolu Dilim (Pay)', style: TextStyle(color: Colors.white70, fontSize: 11)),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.remove_circle_outline, color: Colors.cyanAccent, size: 18),
                      onPressed: _shadedSlices > 1 ? () => setState(() => _shadedSlices--) : null,
                    ),
                    Text('$_shadedSlices', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    IconButton(
                      icon: const Icon(Icons.add_circle_outline, color: Colors.cyanAccent, size: 18),
                      onPressed: _shadedSlices < _fractionSlices ? () => setState(() => _shadedSlices++) : null,
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Dilim Barı
        Container(
          height: 36,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.white24),
          ),
          child: Row(
            children: List.generate(_fractionSlices, (idx) {
              final isShaded = idx < _shadedSlices;
              return Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: isShaded ? Colors.amberAccent.withValues(alpha: 0.6) : Colors.transparent,
                    border: Border(right: BorderSide(color: idx < _fractionSlices - 1 ? Colors.white24 : Colors.transparent)),
                  ),
                  child: Center(
                    child: Text(
                      '1/$_fractionSlices',
                      style: TextStyle(color: isShaded ? Colors.black : Colors.white38, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              );
            }),
          ),
        ),
        const SizedBox(height: 10),
        Text(
          'Kesir Değeri = $_shadedSlices / $_fractionSlices (${((_shadedSlices / _fractionSlices) * 100).toStringAsFixed(0)}%)',
          style: const TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 12),
        ),
      ],
    );
  }

  // ==========================================
  // 3. TERAZİ MODELİ
  // ==========================================
  Widget _buildBalanceScaleCanvas() {
    // 2x + leftWeight = rightWeight
    final int leftTotal = 2 * _boxValue + _leftWeight;
    final bool isBalanced = leftTotal == _rightWeight;
    final currentEq = _leftWeight == 0
        ? "2x = $_rightWeight"
        : "2x + $_leftWeight = $_rightWeight";

    return Column(
      children: [
        // Eşzamanlı Çift Yönlü Cebirsel Denklem Kartı
        Container(
          key: const Key('dynamic_algebraic_equation_card'),
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFF0F172A),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.5)),
          ),
          child: Column(
            children: [
              const Text(
                "Eşzamanlı Cebirsel Denklem (Çift Yönlü Yansıma)",
                style: TextStyle(color: Colors.white70, fontSize: 11),
              ),
              const SizedBox(height: 4),
              Text(
                _leftWeight == 0
                    ? "2x = $_rightWeight  =>  x = ${_rightWeight ~/ 2}"
                    : currentEq,
                key: const Key('dynamic_algebraic_equation_text'),
                style: const TextStyle(
                  color: Colors.cyanAccent,
                  fontFamily: 'monospace',
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
        // Çift Kodlama Canlı Senkronizasyon Rozeti
        Container(
          key: const Key('dual_coding_sync_badge'),
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: const Color(0xFF0284C7).withValues(alpha: 0.18),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFF38BDF8)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.sync_alt, color: Color(0xFF38BDF8), size: 14),
              const SizedBox(width: 6),
              Text(
                _lastDualAction != null
                    ? 'Çift Kodlama Senkronizasyonu: Terazi ➔ Touchpad ($_lastDualAction uygulandı)'
                    : 'Çift Kodlama: Canlı Senkronizasyon ve Dokunsal Eşleşme Aktif',
                style: const TextStyle(
                  color: Color(0xFF38BDF8),
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: isBalanced ? Colors.greenAccent.withValues(alpha: 0.15) : Colors.redAccent.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: isBalanced ? Colors.greenAccent : Colors.redAccent),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              Text('Sol Kefe: 2x + $_leftWeight', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
              Icon(isBalanced ? Icons.check : Icons.warning_amber, color: isBalanced ? Colors.greenAccent : Colors.redAccent, size: 16),
              Text('Sağ Kefe: $_rightWeight', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Terazi Kollarının Görsel Temsili (İskele Solma Destekli)
        AnimatedOpacity(
          key: const Key('balance_scale_manipulatives'),
          duration: const Duration(milliseconds: 300),
          opacity: widget.scaffoldOpacity.clamp(0.1, 1.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              // Sol Kefe
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.blueAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(8)),
                child: Column(
                  children: [
                    const Text('2x Kutusu', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text('+ $_leftWeight Ağırlık', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                  ],
                ),
              ),
              const Icon(Icons.balance, color: Colors.amberAccent, size: 36),
              // Sağ Kefe
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.purpleAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(8)),
                child: Column(
                  children: [
                    const Text('Sabit Sayı', style: TextStyle(color: Colors.purpleAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text('$_rightWeight Ağırlık', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        // İki taraftan aynı ağırlığı çıkarma butonu
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: _leftWeight > 0 && _rightWeight >= 3
                  ? () => setState(() {
                        HapticFeedbackService().mediumImpact();
                        _leftWeight -= 3;
                        _rightWeight -= 3;
                        _lastDualAction = '- 3';
                        widget.onEquationChanged?.call(
                          _leftWeight == 0 ? "2x = $_rightWeight" : "2x + $_leftWeight = $_rightWeight",
                        );
                        widget.onDualCodingAction?.call('- 3');
                      })
                  : null,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.amberAccent, foregroundColor: Colors.black),
              child: const Text('Her İki Kefeden 3 Eksilt (-3)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
            ),
            if (_leftWeight != 3 || _rightWeight != 11) ...[
              const SizedBox(width: 8),
              OutlinedButton.icon(
                key: const Key('btn_reset_balance'),
                onPressed: () => setState(() {
                  HapticFeedbackService().selectionClick();
                  _leftWeight = 3;
                  _rightWeight = 11;
                  _lastDualAction = null;
                  widget.onEquationChanged?.call("2x + $_leftWeight = $_rightWeight");
                  widget.onDualCodingAction?.call('reset');
                }),
                icon: const Icon(Icons.replay, size: 14, color: Colors.white70),
                label: const Text('Sıfırla', style: TextStyle(color: Colors.white70, fontSize: 12)),
                style: OutlinedButton.styleFrom(side: const BorderSide(color: Colors.white24)),
              ),
            ],
          ],
        ),
      ],
    );
  }
}
