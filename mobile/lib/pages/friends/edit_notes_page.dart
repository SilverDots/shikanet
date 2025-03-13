import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class EditNotesPage extends ConsumerStatefulWidget {
  const EditNotesPage({
    super.key,
    required this.uuid,
    required this.friend
  });

  final String uuid;
  final Friend friend;

  @override
  ConsumerState<EditNotesPage> createState() => _EditNotesPageState();
}

class _EditNotesPageState extends ConsumerState<EditNotesPage> {
  late TextEditingController notesController;
  bool buttonEnabled = false;

  @override
  void initState() {
    super.initState();
    notesController = TextEditingController(text: widget.friend.notes);
  }
  
  @override
  void dispose() {
    notesController.dispose();
    super.dispose();
  }

  void canSubmit() {
    setState(() => buttonEnabled = notesController.text != widget.friend.notes);
  }

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.colorScheme.primaryContainer,
        actionsIconTheme: IconThemeData(
          color: theme.colorScheme.onPrimary
        ),
        actions: [
          TextButton(
            onPressed: buttonEnabled ?
              () {
                ref.read(friendsProvider.notifier).updateFriend(
                  widget.uuid, widget.friend.copyWith(notes: notesController.text)
                );
                Navigator.pop(context);
              }
              :
              null,
            style: TextButton.styleFrom(
              foregroundColor: theme.highlightColor
            ),
            child: Text(
              'Done',
              style: TextStyle(
                color: buttonEnabled ?
                theme.colorScheme.onPrimaryContainer
                :
                theme.disabledColor
              )
            ),
          ),
        ],
        title: Text(
          'Edit Notes',
          style: TextStyle(color: theme.colorScheme.onPrimaryContainer, fontWeight: FontWeight.bold)
        ),
        centerTitle: true,
        leading: IconButton(
          onPressed: () => Navigator.pop(context),
          icon: Icon(Icons.arrow_back, color: theme.colorScheme.onPrimaryContainer)
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
        child: Column(
          children: [
            EditProfileTextField(
              name: 'Notes',
              initValue: widget.friend.notes,
              optional: true,
              controller: notesController,
              onChange: (val) => canSubmit(),
              maxLines: 6,
              hintText: 'Tap to enter notes',
              keyboardType: TextInputType.multiline,
            )
          ],
        ),
      )
    );
  }
}