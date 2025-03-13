import 'package:flutter/material.dart';

class FriendDetailCard extends StatelessWidget{
  const FriendDetailCard({
    super.key,
    required this.title,
    required this.fieldValue
  });

  final Widget title;
  final String fieldValue;

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Card(
        color: theme.canvasColor,
        elevation: 0,
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              title,
              SizedBox(height: 6),
              if (fieldValue.isNotEmpty)
                Text(fieldValue)
            ],
          ),
        )
      ),
    );
  }
}