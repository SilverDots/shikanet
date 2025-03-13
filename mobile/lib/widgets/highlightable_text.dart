import 'package:flutter/material.dart';

class HighlightableText extends StatefulWidget {
  const HighlightableText({
    super.key,
    required this.text,
    required this.onTap
  });

  final String text;
  final Function() onTap;

  @override
  State<HighlightableText> createState() => _HighlightableText();
}

class _HighlightableText extends State<HighlightableText> {
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
      child: Text(
        widget.text,
        style: TextStyle(
          color: selected ?
            theme.colorScheme.inversePrimary
            :
            theme.colorScheme.primary,
          fontWeight: FontWeight.bold
        )
      ),
    );
  }
}