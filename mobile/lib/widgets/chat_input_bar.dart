import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';

class ChatInputBar extends ConsumerStatefulWidget {
  const ChatInputBar({super.key});

  @override
  ConsumerState<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends ConsumerState<ChatInputBar> {
  late bool canSubmit;

  // Note that ChatInputBar needs to be a (Consumer)StatefulWidget
  // so that we can read providers in its initState() function before
  // the widget builds.
  @override
  void initState() {
    var textController = ref.read(chatFieldTextProvider);
    canSubmit = textController.text.isNotEmpty;
    super.initState();
  }
  
  @override
  Widget build(BuildContext context) {
    TextEditingController textController = ref.watch(chatFieldTextProvider);
    var theme = Theme.of(context);

    return Row(
      children: [
        SizedBox(width: 12),
        Expanded(
          child: TextField(
            controller: textController,
            onTapOutside: (event) => FocusManager.instance.primaryFocus?.unfocus(),
            decoration: InputDecoration(
              filled: true,
              hintText: 'Search for answers',
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(30),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(30),
                borderSide: BorderSide.none,
              ),
            ),
            minLines: 1,
            maxLines: 5,
            keyboardType: TextInputType.multiline,
            onChanged: (value) {
              textController.text = value;
              setState(() => canSubmit = value.isNotEmpty);
            }
          ),
        ),
        SizedBox(width: 16),
        Theme(
          // data: Theme.of(context).copyWith(highlightColor: darkred),
          data: Theme.of(context),
          child: FloatingActionButton(
            onPressed: canSubmit ?
              () {
                User user = ref.read(userInfoProvider);
                ref.read(chatLogProvider.notifier)
                  .addMessage(textController.text, true, DateTime.now());
                if (!user.appPreferences['pauseHistory']) {
                  ref.read(questionLogProvider.notifier)
                    .addQuestion(textController.text);
                }
                textController.clear();
                setState(() => canSubmit = false);
              } : null,
            elevation: 0,
            focusElevation: 0,
            hoverElevation: 0, 
            highlightElevation: 0,
            backgroundColor: canSubmit ? theme.colorScheme.secondaryContainer : theme.disabledColor,
            foregroundColor: theme.colorScheme.onSecondaryContainer,
            focusColor: Colors.lightGreen,
            hoverColor: Colors.lightGreen,
            splashColor: Colors.transparent,
            shape: CircleBorder(),
            child: const Icon(FontAwesomeIcons.paperPlane)
          ),
        ),
        SizedBox(width: 12)
      ],
    );
  }
}