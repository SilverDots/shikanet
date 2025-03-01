import 'package:flutter/material.dart';
import 'package:shikanet/utils/utils.dart';
import 'package:shikanet/widgets/widgets.dart';

class ShortcutButton extends StatefulWidget {
  const ShortcutButton({super.key, required this.text, required this.icon, required this.onTap});

  final String text;
  final Icon icon;
  final Function() onTap;

  @override
  State<ShortcutButton> createState() => _ShortcutButtonState();
}

class _ShortcutButtonState extends State<ShortcutButton> {
  bool selected = false;

  @override
  Widget build(BuildContext context) {
    return AnimatedCardButton(
      onTap: widget.onTap,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            widget.icon,
            SizedBox(height: 20),
            Text(
              widget.text,
              style: TextStyle(
                fontFamily: 'Roboto',
                fontSize: 20,
                color: lightyellow,
              ),
            )
          ]
        ),
      )
    );
  }
}