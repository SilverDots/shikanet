import 'package:flutter/material.dart';

class SettingsHeading extends StatelessWidget {
  const SettingsHeading({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Text(
        title,
        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)
      )
    );
  }
}