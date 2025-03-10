import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';

class HomeTitleCard extends ConsumerWidget {
  const HomeTitleCard({super. key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    var theme = Theme.of(context);
    User user = ref.watch(userInfoProvider);
    
    return Card(
      color: theme.colorScheme.primary,
      child: Row(
        children: [
          Flexible(
            flex: 4,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 30),
              child: ListTile(
                title: Text('Hello, ${user.firstName}'),
                subtitle: Text("Ask questions, view your recent searches, and more."),
                titleTextStyle: TextStyle(
                  fontFamily: 'Roboto',
                  fontWeight: FontWeight.bold,
                  fontSize: 30,
                  color: theme.colorScheme.onPrimary,
                ),
                subtitleTextStyle: TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onPrimary,
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