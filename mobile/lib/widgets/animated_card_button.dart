import 'package:flutter/material.dart';

class AnimatedCardButton extends StatefulWidget {
  const AnimatedCardButton({
    super.key,
    required this.child,
    required this.onTap,
    this.backgroundColor,
    this.highlightColor,
    this.borderRadius,
    this.padding = const EdgeInsets.all(4.0),
    this.shadow = true
  });

  final Widget child;
  final Function() onTap;
  final Color? backgroundColor;
  final Color? highlightColor;
  final BorderRadius? borderRadius;
  final EdgeInsets padding;
  final bool shadow;

  @override
  State<AnimatedCardButton> createState() => _AnimatedCardButtonState();
}

class _AnimatedCardButtonState extends State<AnimatedCardButton> {
  bool selected = false;

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);

    return InkWell(
      onTap: widget.onTap,
      onHighlightChanged: (value) {
        setState(() => selected = value);
      },
      highlightColor: Colors.transparent,
      splashColor: Colors.transparent,
      child: Padding(
        padding: widget.padding,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          curve: Curves.easeInOut,
          decoration: BoxDecoration(
            borderRadius: widget.borderRadius ?? BorderRadius.circular(12),
            color: selected ?
              widget.highlightColor ?? theme.colorScheme.secondaryFixedDim
              :
              widget.backgroundColor ?? theme.colorScheme.secondaryContainer,
            boxShadow: [
              if (widget.shadow)
                BoxShadow(
                  color: theme.colorScheme.shadow,
                  blurRadius: 1,
                  spreadRadius: 0,
                  offset: Offset(0, 2),
                ),
            ],
          ),
          child: widget.child
        ),
      ),
    );
  }
}