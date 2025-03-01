import 'package:flutter/material.dart';
import 'package:shikanet/utils/utils.dart';

class AnimatedCardButton extends StatefulWidget {
  const AnimatedCardButton({super.key, required this.child, required this.onTap});

  final Widget child;
  final Function() onTap;

  @override
  State<AnimatedCardButton> createState() => _AnimatedCardButtonState();
}

class _AnimatedCardButtonState extends State<AnimatedCardButton> {
  bool selected = false;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: widget.onTap,
      onHighlightChanged: (value) {
        setState(() => selected = value);
      },
      highlightColor: Colors.transparent,
      splashColor: Colors.transparent,
      child: Padding(
        padding: const EdgeInsets.all(4.0),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          curve: Curves.easeInOut,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: selected ? darkerred : black,
            boxShadow: [
              BoxShadow(
                color: Colors.grey,
                blurRadius: 2,
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