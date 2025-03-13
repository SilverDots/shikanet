import 'package:flutter/material.dart';

class TitleCard extends StatelessWidget {
  const TitleCard({
    super.key,
    required this.title,
    this.subtitle,
    this.padding = const EdgeInsets.symmetric(vertical: 30),
    this.backgroundColor,
    this.textColor
  });

  final String title;
  final String? subtitle;
  final Color? backgroundColor;
  final Color? textColor;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);
    
    return Card(
      color: backgroundColor ?? theme.colorScheme.primary,
      child: Row(
        children: [
          Flexible(
            flex: 4,
            child: Padding(
              padding: padding,
              child: ListTile(
                title: Text(title),
                subtitle: subtitle != null ? Text(subtitle!) : null,
                titleTextStyle: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 30,
                  color: textColor ?? theme.colorScheme.onPrimary,
                ),
                subtitleTextStyle: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: textColor ?? theme.colorScheme.onPrimary,
                  height: 1.75
                ),
              ),
            ),
          ),
          Spacer()
        ],
      ),
    );
  }
}