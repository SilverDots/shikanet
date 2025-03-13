import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/utils/utils.dart';
import 'package:shikanet/widgets/widgets.dart';

var resetExplanation =
"""
Erasing all content will clear your search and chat history.
Resetting all settings will restore app preferences to default settings.
""".trim().replaceAll("\n", " ");

class ManageHistoryPage extends ConsumerStatefulWidget {
  const ManageHistoryPage({super.key});

  @override
  ConsumerState<ManageHistoryPage> createState() => _ManageHistoryPageState();
}

class _ManageHistoryPageState extends ConsumerState<ManageHistoryPage> {
  late bool pauseSearchHistory;
  
  @override
  void initState() {
    super.initState();
    pauseSearchHistory = ref.read(userInfoProvider).appPreferences['pauseHistory'];
  }
  
  @override
  Widget build(BuildContext context) {
    Widget divider = Divider(indent: 12, height: 0);
    var theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () {
            Navigator.pop(context);
          },
          icon: Icon(Icons.arrow_back, color: theme.colorScheme.onSurface)
        ),
        backgroundColor: theme.colorScheme.surfaceContainerHigh,
        centerTitle: true,
        title: Text(
          'Manage History',
          style: TextStyle(color: theme.colorScheme.onSurface, fontWeight: FontWeight.w500)
        )
      ),
      body: ListView(
        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 26),
        children: [
          SettingsHeading(title: 'Search History'),
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.only(
                topLeft: const Radius.circular(12),
                topRight: const Radius.circular(12), 
              ),
              color: theme.colorScheme.surfaceContainer
            ),
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 12),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      'Pause search history',
                      style: Theme.of(context).textTheme.bodyLarge
                    ),
                  ),
                  Switch(
                    value: pauseSearchHistory,
                    onChanged: (value) {
                      User user = ref.read(userInfoProvider);
                      ref.read(userInfoProvider.notifier).update(
                        user.copyWith(appPreferences: {'pauseHistory' : value})
                      );
                      setState(() => pauseSearchHistory = value);
                    }
                  )
                ],
              )
            )
          ),
          divider,
          FullWidthButton(
            title: 'Clear search history',
            borderRadius: BorderRadius.only(
              bottomLeft: const Radius.circular(12),
              bottomRight: const Radius.circular(12)
            ),
            textColor: theme.colorScheme.error,
            contentPadding: EdgeInsets.symmetric(horizontal: 12),
            onTap: () =>
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: Text('Clear search history?'),
                  content: Text(
                    'Are you sure you want to clear your search history? This action cannot be undone.'
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, 'Cancel'),
                      child: const Text('Cancel'),
                    ),
                    TextButton(
                      onPressed: () {
                        ref.read(questionLogProvider.notifier).clear();
                        Navigator.pop(context, 'Proceed');
                      },
                      child: const Text('Proceed', style: TextStyle(color: Colors.red)),
                    ),
                  ]
                )
              )
          ),
          SizedBox(height: 10),
          SettingsHeading(title: "General"),
          FullWidthButton(
            title: 'Clear chat history',
            borderRadius: BorderRadius.only(
              topLeft: const Radius.circular(12),
              topRight: const Radius.circular(12)
            ),
            textColor: Colors.blue,
            contentPadding: EdgeInsets.symmetric(horizontal: 12),
            onTap: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: Text('Clear chat history?'),
                  content: Text(
                    'Are you sure you want to clear your chat history? This action cannot be undone.'
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, 'Cancel'),
                      child: const Text('Cancel'),
                    ),
                    TextButton(
                      onPressed: () {
                        ref.read(chatLogProvider.notifier).reset();
                        Navigator.pop(context, 'Proceed');
                      },
                      child: const Text('Proceed', style: TextStyle(color: Colors.red)),
                    ),
                  ]
                )
              );
            }
          ),
          divider,
          FullWidthButton(
            title: 'Erase all content and reset settings',
            borderRadius: BorderRadius.only(
              bottomLeft: const Radius.circular(12),
              bottomRight: const Radius.circular(12)
            ),
            textColor: theme.colorScheme.error,
            contentPadding: EdgeInsets.symmetric(horizontal: 12),
            onTap: () =>
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: Text('Erase all content and reset settings?'),
                  content: Text(
                    'Are you sure you want to erase all contents and reset settings? This action cannot be undone.'
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, 'Cancel'),
                      child: const Text('Cancel'),
                    ),
                    TextButton(
                      onPressed: () {
                        User user = ref.read(userInfoProvider);
                        
                        ref.read(questionLogProvider.notifier).clear();
                        ref.read(chatLogProvider.notifier).reset();
                        ref.read(userInfoProvider.notifier).update(
                          user.copyWith(appPreferences: defaultPreferences)
                        );
                        setState(() => pauseSearchHistory = false);
                        Navigator.pop(context, 'Proceed');
                      },
                      child: const Text('Proceed', style: TextStyle(color: Colors.red)),
                    ),
                  ]
                )
              )
          ),
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: Text(resetExplanation)
          )
        ],
      )
    );
  }
}