import 'package:flutter/material.dart';

/// Hareket Problemleri için Dinamik Zaman-Yol ve Bağıl Hız Görselleştiricisi.
class MotionDiagramWidget extends StatelessWidget {
  final double distanceKm;
  final String vehicle1Name;
  final double vehicle1Speed;
  final String vehicle2Name;
  final double vehicle2Speed;
  final bool isOppositeDirection; // true: karşılıklı karşılaşma, false: yakalama
  final double? meetingTimeHours;

  const MotionDiagramWidget({
    super.key,
    this.distanceKm = 400.0,
    this.vehicle1Name = 'A Aracı',
    this.vehicle1Speed = 60.0,
    this.vehicle2Name = 'B Aracı',
    this.vehicle2Speed = 40.0,
    this.isOppositeDirection = true,
    this.meetingTimeHours = 4.0,
  });

  /// Fiziksel Gerçeklik: Mesafe kırpma (d >= 0)
  static double clampDistance(double d) => (d.isFinite && d >= 0) ? d : 0.0;

  /// Fiziksel Gerçeklik: Hız kırpma (v > 0)
  static double clampVelocity(double v, {double minVelocity = 0.001}) =>
      (v.isFinite && v > 0) ? v : minVelocity;

  /// Fiziksel Gerçeklik: Zaman kırpma (t >= 0)
  static double clampTime(double t) => (t.isFinite && t >= 0) ? t : 0.0;

  @override
  Widget build(BuildContext context) {
    final double safeDist = clampDistance(distanceKm);
    final double safeV1 = (vehicle1Speed.isFinite && vehicle1Speed >= 0) ? vehicle1Speed : 0.0;
    final double safeV2 = (vehicle2Speed.isFinite && vehicle2Speed >= 0) ? vehicle2Speed : 0.0;
    final double relativeSpeed = isOppositeDirection
        ? (safeV1 + safeV2)
        : (safeV1 - safeV2).abs();
    final double computedTime = relativeSpeed > 0 ? (safeDist / relativeSpeed) : 0;
    final double totalV = safeV1 + safeV2;
    final double meetingRatio = isOppositeDirection
        ? (totalV > 0 ? (safeV1 / totalV).clamp(0.1, 0.9) : 0.5)
        : 0.8;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.directions_car, color: Colors.cyanAccent, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    isOppositeDirection ? 'Karşıt Yönlü Hareket Şeması' : 'Aynı Yönlü Yakalama Şeması',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.cyanAccent.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Yol: ${safeDist.toStringAsFixed(0)} km',
                  style: const TextStyle(
                    color: Colors.cyanAccent,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Yol ve Araç Çizgisi
          SizedBox(
            height: 96,
            child: LayoutBuilder(
              builder: (context, constraints) {
                final double width = constraints.maxWidth;
                final double meetX = width * meetingRatio;

                return Stack(
                  alignment: Alignment.center,
                  children: [
                    // Ana Yol Çizgisi
                    Positioned(
                      left: 20,
                      right: 20,
                      child: Container(
                        height: 4,
                        decoration: BoxDecoration(
                          color: Colors.white24,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ),
                    // Karşılaşma / Hedef Noktası İşareti
                    Positioned(
                      left: meetX - 25,
                      top: 8,
                      child: SizedBox(
                        width: 50,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.location_on, color: Colors.amberAccent, size: 18),
                            Container(
                              width: 2,
                              height: 16,
                              color: Colors.amberAccent,
                            ),
                            const Text(
                              'Karşılaşma',
                              style: TextStyle(color: Colors.amberAccent, fontSize: 9),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ),
                    // Araç 1 (Solda)
                    Positioned(
                      left: 10,
                      top: 4,
                      child: Column(
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.arrow_forward, color: Colors.greenAccent, size: 14),
                              Text(
                                '${safeV1.toStringAsFixed(0)} km/h',
                                style: const TextStyle(color: Colors.greenAccent, fontSize: 11),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          const CircleAvatar(
                            radius: 12,
                            backgroundColor: Colors.greenAccent,
                            child: Icon(Icons.directions_car, color: Colors.black, size: 14),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            vehicle1Name,
                            style: const TextStyle(color: Colors.white70, fontSize: 10),
                          ),
                        ],
                      ),
                    ),
                    // Araç 2 (Sağda veya Geride)
                    Positioned(
                      right: 10,
                      top: 4,
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Icon(
                                isOppositeDirection ? Icons.arrow_back : Icons.arrow_forward,
                                color: Colors.orangeAccent,
                                size: 14,
                              ),
                              Text(
                                '${safeV2.toStringAsFixed(0)} km/h',
                                style: const TextStyle(color: Colors.orangeAccent, fontSize: 11),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          const CircleAvatar(
                            radius: 12,
                            backgroundColor: Colors.orangeAccent,
                            child: Icon(Icons.directions_car, color: Colors.black, size: 14),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            vehicle2Name,
                            style: const TextStyle(color: Colors.white70, fontSize: 10),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          // Dinamik Bağıl Hız ve Formül Çubuğu
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
                  isOppositeDirection
                      ? 'Bağıl Hız = v₁ + v₂ = ${relativeSpeed.toStringAsFixed(0)} km/h'
                      : 'Bağıl Hız = |v₁ - v₂| = ${relativeSpeed.toStringAsFixed(0)} km/h',
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                ),
                Text(
                  't = x / v_bağıl = ${computedTime.toStringAsFixed(1)} saat',
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
}
