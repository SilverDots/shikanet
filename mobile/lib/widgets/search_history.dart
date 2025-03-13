import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class SearchHistory extends ConsumerWidget {
  const SearchHistory({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    List<String> questions = ref.watch(questionLogProvider).toList();
    if (questions.isEmpty) {
      return Padding(
        padding: const EdgeInsets.all(4.0),
        child: Align(
            alignment: Alignment.topLeft,
            child: Text("No searches found.")
          ),
      );
    }
    return SearchHistoryList(history: questions);
  }
}