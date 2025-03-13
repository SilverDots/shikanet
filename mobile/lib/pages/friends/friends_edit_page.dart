import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_libphonenumber/flutter_libphonenumber.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class FriendsEditPage extends ConsumerStatefulWidget {
  const FriendsEditPage({
    super.key,
    required this.uuid,
    this.friend
  });

  final String uuid;
  final Friend? friend;

  @override
  ConsumerState<FriendsEditPage> createState() => _FriendsEditPage();
}

class _FriendsEditPage extends ConsumerState<FriendsEditPage> {
  final _formkey = GlobalKey<FormState>();
  
  late TextEditingController fnameController;
  late TextEditingController lnameController;
  late TextEditingController emailController;
  late TextEditingController phoneController;
  late TextEditingController discordController;
  late TextEditingController whatsAppController;
  late TextEditingController notesController;
  bool buttonEnabled = false;
  
  LibPhonenumberTextFormatter? phoneFormatter;

  @override
  void initState() {
    super.initState();
    if (widget.friend?.phoneNumber != null) {
      updatePhoneFormat(widget.friend!.phoneNumber!);
    }
    fnameController = TextEditingController(text: widget.friend?.firstName);
    lnameController = TextEditingController(text: widget.friend?.lastName);
    emailController = TextEditingController(text: widget.friend?.email);
    phoneController = TextEditingController(text: widget.friend?.phoneNumber);
    discordController = TextEditingController(text: widget.friend?.discordID);
    whatsAppController = TextEditingController(text: widget.friend?.whatsAppID);
    notesController = TextEditingController(text: widget.friend?.notes);
  }

  void canSubmit() {
    if (_formkey.currentState!.validate()) {
      Friend currFriend = inputToFriend();
      setState(() => buttonEnabled = widget.friend != currFriend);
    } else {
      setState(() => buttonEnabled = false);
    }
  }

  void updatePhoneFormat(String val) async {
    if (val.length > 1 && val[0] == '+' && '+'.allMatches(val).length == 1) {
      String code = val.substring(1);
      Map<String, CountryWithPhoneCode> countryMap = await ref.read(phoneFormatterProvider.future);
      for (String country in countryMap.keys) {
        CountryWithPhoneCode? cwpc = countryMap[country];
        if (cwpc != null && cwpc.phoneCode == code) {
          setState(() => phoneFormatter = LibPhonenumberTextFormatter(
            country: cwpc,
            phoneNumberFormat: PhoneNumberFormat.international,
            inputContainsCountryCode: true,
            additionalDigits: 3
          ));
        }
      }
    } else if (val.length == 1 && double.tryParse(val) != null) {
      setState(() => phoneFormatter = LibPhonenumberTextFormatter(
        country: CountryWithPhoneCode.us(),
        phoneNumberFormat: PhoneNumberFormat.national
      ));
    } else if (val.isEmpty) {
      setState(() => phoneFormatter = null);
    }
  }

  Friend inputToFriend() {
    return Friend(
      firstName: fnameController.text,
      lastName: lnameController.text.isEmpty ? null : lnameController.text,
      email: emailController.text.isEmpty ? null : emailController.text,
      phoneNumber: phoneController.text.isEmpty ? null : phoneController.text,
      discordID: discordController.text.isEmpty ? null : discordController.text,
      whatsAppID: whatsAppController.text.isEmpty ? null : whatsAppController.text,
      notes: notesController.text
    );
  }

  @override
  void dispose() {
    fnameController.dispose();
    lnameController.dispose();
    emailController.dispose();
    phoneController.dispose();
    discordController.dispose();
    whatsAppController.dispose();
    notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);

    List<Widget> inputs = [
      EditProfileTextField(
        name: 'First name',
        initValue: widget.friend?.firstName,
        keyboardType: TextInputType.name,
        controller: fnameController,
        onChange: (val) => canSubmit()
      ),
      EditProfileTextField(
        name: 'Last name',
        initValue: widget.friend?.lastName,
        keyboardType: TextInputType.name,
        controller: lnameController,
        onChange: (val) => canSubmit(),
        optional: true,
      ),
      EditProfileTextField(
        name: 'Email',
        initValue: widget.friend?.email,
        keyboardType: TextInputType.emailAddress,
        controller: emailController,
        onChange: (val) => canSubmit(),
        optional: true,
      ),
      EditProfileTextField(
        name: 'Phone number',
        initValue: widget.friend?.phoneNumber,
        keyboardType: TextInputType.phone,
        optional: true,
        onChange: (val) {
          updatePhoneFormat(val);
          canSubmit();
        },
        inputFormatters: [
          if (phoneFormatter != null) phoneFormatter!
        ],
        controller: phoneController
      ),
      EditProfileTextField(
        name: 'Discord ID',
        initValue: widget.friend?.discordID,
        prefix: "@",
        optional: true,
        controller: discordController,
        onChange: (val) => canSubmit()
      ),
      EditProfileTextField(
        name: 'WhatsApp ID',
        initValue: widget.friend?.whatsAppID,
        optional: true,
        controller: whatsAppController,
        onChange: (val) => canSubmit()
      ),
      EditProfileTextField(
        name: 'Notes',
        initValue: widget.friend?.notes,
        optional: true,
        controller: notesController,
        onChange: (val) => canSubmit(),
        maxLines: 6,
        hintText: 'Tap to enter notes',
        keyboardType: TextInputType.multiline,
      )
    ];

    if (widget.friend != null) {
      inputs.add(FullWidthButton(
        title: 'Remove friend',
        textColor: theme.colorScheme.error,
        borderRadius: BorderRadius.circular(12),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12),
        onTap: () {
          // For now, just pop until reaching base Friends
          ref.read(friendsProvider.notifier).removeFriend(widget.uuid);
          Navigator.of(context).popUntil((route) => route.isFirst);
        }
      ));
    }

    return Scaffold(
      appBar: AppBar(
        leadingWidth: 70,
        leading: TextButton(
          onPressed: () {
            Navigator.pop(context);
          },
          style: TextButton.styleFrom(
            foregroundColor: theme.highlightColor
          ),
          child: Text(
            'Cancel',
            style: TextStyle(color: theme.colorScheme.onPrimaryContainer)
          ),
        ),
        backgroundColor: theme.colorScheme.primaryContainer,
        centerTitle: true,
        actions: [
          TextButton(
            onPressed: buttonEnabled ?
              () {
                ref.read(friendsProvider.notifier).updateFriend(
                  widget.uuid, inputToFriend()
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
          'Edit Friend Profile',
          style: TextStyle(color: theme.colorScheme.onPrimaryContainer, fontWeight: FontWeight.bold))
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Form(
          key: _formkey,
          child: ListView.separated(
            padding: EdgeInsets.only(
              top: 30,
              bottom: 30
            ),
            itemBuilder: (context, idx) => inputs[idx],
            separatorBuilder: (context, idx) => SizedBox(height: 30),
            itemCount: inputs.length)
        ),
      )
    );
  }
}