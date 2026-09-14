import 'package:flutter/material.dart';

/// Karışım Problemleri için Kap ve Konsantrasyon Şeması (Bruner E-I-S Iconic)
class MixtureVesselWidget extends StatelessWidget {
  final double volume1;
  final double percentage1;
  final double volume2;
  final double percentage2;
  final String soluteName;

  const MixtureVesselWidget({
    super.key,
    this.volume1 = 40.0,
    this.percentage1 = 20.0,
    this.volume2 = 60.0,
    this.percentage2 = 50.0,
    this.soluteName = 'Tuz',
  });

  @override
  Widget build(BuildContext context) {
    final double totalVolume = volume1 + volume2;
    final double totalSolute = (volume1 * (percentage1 / 100)) + (volume2 * (percentage2 / 100));
    final double finalPercentage = totalVolume > 0 ? (totalSolute / totalVolume) * 100 : 0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.science, color: Colors.purpleAccent, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Karışım ve Kap Denge Şeması ($soluteName)',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.purpleAccent.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Toplam: ${totalVolume.toStringAsFixed(0)} L',
                  style: const TextStyle(
                    color: Colors.purpleAccent,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // 3 Kap Yan Yana
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              _buildVesselCard(
                label: '1. Kap',
                volume: volume1,
                percentage: percentage1,
                soluteAmount: volume1 * (percentage1 / 100),
                color: Colors.blueAccent,
              ),
              const Text(
                '+',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
              _buildVesselCard(
                label: '2. Kap',
                volume: volume2,
                percentage: percentage2,
                soluteAmount: volume2 * (percentage2 / 100),
                color: Colors.tealAccent,
              ),
              const Text(
                '=',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
              _buildVesselCard(
                label: 'Karışım',
                volume: totalVolume,
                percentage: finalPercentage,
                soluteAmount: totalSolute,
                color: Colors.amberAccent,
                isResult: true,
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.black38,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Text(
                  'Saf Madde Dengesi: ${volume1.toStringAsFixed(0)}·%${percentage1.toStringAsFixed(0)} + ${volume2.toStringAsFixed(0)}·%${percentage2.toStringAsFixed(0)}',
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                ),
                Text(
                  'Nihai Yüzde: %${finalPercentage.toStringAsFixed(1)}',
                  style: const TextStyle(
                    color: Colors.amberAccent,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVesselCard({
    required String label,
    required double volume,
    required double percentage,
    required double soluteAmount,
    required Color color,
    bool isResult = false,
  }) {
    final double fillRatio = (percentage / 100.0).clamp(0.15, 1.0);

    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            color: isResult ? Colors.amberAccent : Colors.white70,
            fontSize: 11,
            fontWeight: isResult ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        const SizedBox(height: 6),
        // Beaker Şekli
        Container(
          width: 54,
          height: 70,
          decoration: BoxDecoration(
            color: Colors.white10,
            borderRadius: const BorderRadius.only(
              bottomLeft: Radius.circular(10),
              bottomRight: Radius.circular(10),
            ),
            border: Border.all(color: color.withValues(alpha: 0.6), width: 2),
          ),
          child: Stack(
            alignment: Alignment.bottomCenter,
            children: [
              FractionallySizedBox(
                heightFactor: fillRatio,
                widthFactor: 1.0,
                child: Container(
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.35),
                    borderRadius: const BorderRadius.only(
                      bottomLeft: Radius.circular(8),
                      bottomRight: Radius.circular(8),
                    ),
                  ),
                ),
              ),
              Center(
                child: Text(
                  '%${percentage.toStringAsFixed(0)}',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 6),
        Text(
          '${volume.toStringAsFixed(0)} L',
          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
        ),
        Text(
          '(${soluteAmount.toStringAsFixed(1)} L $soluteName)',
          style: const TextStyle(color: Colors.white38, fontSize: 9),
        ),
      ],
    );
  }
}
