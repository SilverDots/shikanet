import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/pages/pages.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class FriendsPage extends ConsumerWidget {
  const FriendsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    Map<String, Friend> friends = ref.watch(friendsProvider);
    List<(String, Friend)> friendsList = [];
    friends.forEach((key, value) => friendsList.add((key, value)));
    friendsList.sort((a, b) => a.$2.firstName.compareTo(b.$2.firstName));
    var theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        centerTitle: true,
        title: Text(
          "Friends",
          style: TextStyle(
            color: theme.colorScheme.onPrimaryContainer,
            fontWeight: FontWeight.bold
          )
        ),
        backgroundColor: theme.colorScheme.primaryContainer,
        actionsIconTheme: IconThemeData(
          color: theme.colorScheme.onPrimaryContainer
        ),
        actions: [
          IconButton(
            onPressed: () {
              Navigator.of(context).push(MaterialPageRoute(
                builder:(context) {
                  return FriendsEditPage(uuid: Uuid().v4());
                },
              ));
            },
            icon: Icon(Icons.person_add),
          )
        ],
      ),
      body: friends.isEmpty ?
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 30),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'You have no friends.',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)
              ),
              Text('At least, not yet..!')
            ],
          ),
        )
        :
        ListView.separated(
          padding: EdgeInsets.symmetric(vertical: 30),
          separatorBuilder:(context, index) => const Divider(height: 0),
          itemBuilder:(context, index) {
            (String, Friend) record = friendsList[index];
            return FullWidthButton(
              title: record.$2.lastName != null ?
                '${record.$2.firstName} ${record.$2.lastName}'
                :
                record.$2.firstName,
              onTap: () {
                Navigator.of(context).push(MaterialPageRoute(
                  builder:(context) {
                    return FriendsDetailsPage(uuid: record.$1);
                  },
                ));
              }
            );
          },
          itemCount: friends.length,
        ),
    );
  }
}