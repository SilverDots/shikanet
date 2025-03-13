import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/widgets/widgets.dart';

class SearchHistoryList extends ConsumerWidget {
  const SearchHistoryList({super.key, required this.history});

  final List<String> history;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      children: [
        for (String question in history)
          SearchHistoryCard(data: question)
      ]
    );
  }
}