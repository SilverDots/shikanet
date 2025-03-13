import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:math';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/pages/pages.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class FriendsDetailsPage extends ConsumerWidget {
  const FriendsDetailsPage({super.key, required this.uuid});

  final String uuid;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    Friend? friend = ref.watch(friendsProvider)[uuid];
    if (friend == null) {
      return Text('Will not show up.');
    }
    var theme = Theme.of(context);
    TextStyle boldStyle = const TextStyle(fontWeight: FontWeight.bold);
    
    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.colorScheme.primaryContainer,
        actionsIconTheme: IconThemeData(
          color: theme.colorScheme.onPrimary
        ),
        title: Text(
          friend.lastName != null ?
            "${friend.firstName} ${friend.lastName}"
            :
            friend.firstName,
          style: TextStyle(color: theme.colorScheme.onPrimaryContainer, fontWeight: FontWeight.bold)
        ),
        centerTitle: true,
        leading: IconButton(
          onPressed: () => Navigator.pop(context),
          icon: Icon(Icons.arrow_back, color: theme.colorScheme.onPrimaryContainer)
        ),
        actions: [
          IconButton(
            onPressed: () {
              Navigator.of(context).push(MaterialPageRoute(
                builder: (context) => FriendsEditPage(
                  uuid: uuid, friend: friend
                ),
              ));
            },
            icon: Icon(Icons.edit, color: theme.colorScheme.onPrimaryContainer,)
          )
        ],
      ),
      backgroundColor: theme.colorScheme.surfaceContainerHigh,
      body: ListView(
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 24),
        children: [
          if (friend.email != null)
            FriendDetailCard(
              title: Text('Email', style: boldStyle),
              fieldValue: friend.email!
            ),
          if (friend.phoneNumber != null)
            FriendDetailCard(
              title: Text('Phone', style: boldStyle),
              fieldValue: friend.phoneNumber!
            ),
          if (friend.discordID != null)
            FriendDetailCard(
              title: Text('Discord', style: boldStyle),
              fieldValue: friend.discordID!
            ),
          if (friend.whatsAppID != null)
            FriendDetailCard(
              title: Text('WhatsApp', style: boldStyle),
              fieldValue: friend.whatsAppID!
            ),
          FriendDetailCard(
            title: Row(
              children: [
                Text('Notes', style: boldStyle),
                Spacer(),
                Transform.rotate(
                  angle: 90 * pi / 180,
                  child: IconButton(
                    onPressed: () {
                      Navigator.of(context).push(MaterialPageRoute(
                        builder:(context) => EditNotesPage(uuid: uuid, friend: friend),
                      ));
                    },
                    visualDensity: VisualDensity.compact,
                    icon: Icon(
                      Icons.add_chart,
                      color: theme.colorScheme.onSurface
                    )
                  )
                )
              ],
            ),
            fieldValue: friend.notes
          )
        ],
      )
    );
  }
}