import 'package:flutter/material.dart';
import 'dart:math';

class TypingIndicator extends StatefulWidget {
  const TypingIndicator({
    super.key,
    this.bubbleColor = const Color(0xFF646b7f),
    this.flashingCircleDarkColor = const Color(0xFF333333),
    this.flashingCircleBrightColor = const Color(0xFFaec1dd),
  });

  final Color bubbleColor;
  final Color flashingCircleDarkColor;
  final Color flashingCircleBrightColor;

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with TickerProviderStateMixin {
  late AnimationController _repeatingController;
  final List<Interval> _dotIntervals = const [
    Interval(0.25, 0.8),
    Interval(0.35, 0.9),
    Interval(0.45, 1.0),
  ];

  @override
  void initState() {
    super.initState();

    _repeatingController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );

    _repeatingController.repeat();
  }

  @override
  void dispose() {
    _repeatingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _StatusBubble(
      repeatingController: _repeatingController,
      dotIntervals: _dotIntervals,
      flashingCircleDarkColor: widget.flashingCircleDarkColor,
      flashingCircleBrightColor: widget.flashingCircleBrightColor,
      bubbleColor: widget.bubbleColor,
    );
  }
}

class _StatusBubble extends StatelessWidget {
  const _StatusBubble({
    required this.repeatingController,
    required this.dotIntervals,
    required this.flashingCircleBrightColor,
    required this.flashingCircleDarkColor,
    required this.bubbleColor,
  });

  final AnimationController repeatingController;
  final List<Interval> dotIntervals;
  final Color flashingCircleDarkColor;
  final Color flashingCircleBrightColor;
  final Color bubbleColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 60,
      padding: const EdgeInsets.all(4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          for (int i = 0; i < 3; i++)
            _FlashingCircle(
              index: i,
              repeatingController: repeatingController,
              dotIntervals: dotIntervals,
              flashingCircleDarkColor: flashingCircleDarkColor,
              flashingCircleBrightColor: flashingCircleBrightColor,
            )
        ],
      )
    );
  }
}

class _FlashingCircle extends StatelessWidget {
  const _FlashingCircle({
    required this.index,
    required this.repeatingController,
    required this.dotIntervals,
    required this.flashingCircleBrightColor,
    required this.flashingCircleDarkColor,
  });

  final int index;
  final AnimationController repeatingController;
  final List<Interval> dotIntervals;
  final Color flashingCircleDarkColor;
  final Color flashingCircleBrightColor;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: repeatingController,
      builder: (context, child) {
        final circleFlashPercent = dotIntervals[index].transform(
          repeatingController.value,
        );
        final circleColorPercent = sin(pi * circleFlashPercent);

        return Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Color.lerp(
              flashingCircleDarkColor,
              flashingCircleBrightColor,
              circleColorPercent,
            ),
          ),
        );
      },
    );
  }
}