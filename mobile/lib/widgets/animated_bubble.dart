import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';

class AnimatedBubble extends ConsumerStatefulWidget {
  const AnimatedBubble({
    super.key,
    required this.child,
    required this.duration,
    this.message,
    required this.alignment  
  });

  final Widget child;
  final Duration duration;
  final Message? message;
  final Alignment alignment;

  @override
  ConsumerState<AnimatedBubble> createState() => _AnimatedBubbleState();
}

class _AnimatedBubbleState extends ConsumerState<AnimatedBubble>
    with TickerProviderStateMixin {
  
  late AnimationController appearanceController;
  late Animation<double> bubbleAnimation;

  @override
  void initState() {
    super.initState();
    appearanceController = AnimationController(vsync: this);

    appearanceController
      ..duration = widget.duration
      ..forward();

    appearanceController.addStatusListener((status) {
      if (widget.message != null && status == AnimationStatus.completed) {
        ref.read(chatLogProvider.notifier).markRendered(widget.message!);
      }
    });

    bubbleAnimation = CurvedAnimation(
      parent: appearanceController,
      curve: const Interval(0.2, 1.0, curve: Curves.elasticOut),
      // reverseCurve: const Interval(0.7, 1.0, curve: Curves.easeOut),
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
          alignment: widget.alignment,
          child: child,
        );
      },
      child: widget.child
    );
  }
}