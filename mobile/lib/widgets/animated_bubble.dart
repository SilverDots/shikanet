import 'package:flutter/material.dart';

class AnimatedBubble extends StatefulWidget {
  const AnimatedBubble({super.key, required this.child});

  final Widget child;

  @override
  State<StatefulWidget> createState() => _AnimatedBubbleState();
}

class _AnimatedBubbleState extends State<AnimatedBubble>
    with TickerProviderStateMixin {
  
  late AnimationController appearanceController;
  late Animation<double> bubbleAnimation;

  @override
  void initState() {
    super.initState();
    appearanceController = AnimationController(vsync: this);

    appearanceController
      ..duration = const Duration(milliseconds: 750)
      ..forward();

    bubbleAnimation = CurvedAnimation(
      parent: appearanceController,
      curve: const Interval(0.3, 1.0, curve: Curves.elasticOut),
      reverseCurve: const Interval(0.5, 1.0, curve: Curves.easeOut),
    );
  }

  @override
  void dispose() {
    appearanceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: bubbleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: bubbleAnimation.value,
          alignment: Alignment.bottomRight,
          child: child,
        );
      },
      child: widget.child
    );
  }
}