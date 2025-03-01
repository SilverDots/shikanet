import 'package:flutter/material.dart';
import 'package:shikanet/utils/utils.dart';

class SectionHeading extends StatelessWidget {
  const SectionHeading({super.key, required this.heading});

  final String heading;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(4),
      child: Align(
        alignment: Alignment.topLeft,
        child: Text(
          heading,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: black
          ),
        ),
      ),
    );
  }
}