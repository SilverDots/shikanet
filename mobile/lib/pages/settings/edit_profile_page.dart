import 'package:flutter/material.dart';
import 'package:flutter_libphonenumber/flutter_libphonenumber.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:top_snackbar_flutter/top_snack_bar.dart';
import 'package:top_snackbar_flutter/custom_snack_bar.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

var helpText = 
"""
Update your profile below. Any updates to your profile will be 
reflected in your searches. Completing more of your profile may 
improve the quality of your search results.
""".trim().replaceAll("\n", "");

class EditProfilePage extends ConsumerStatefulWidget {
  const EditProfilePage({super.key});

  @override
  ConsumerState<EditProfilePage> createState() => _EditProfilePageState();
}

class _EditProfilePageState extends ConsumerState<EditProfilePage> {
  final _formkey = GlobalKey<FormState>();

  late TextEditingController fnameController;
  late TextEditingController lnameController;
  late TextEditingController emailController;
  late TextEditingController phoneController;
  late TextEditingController discordController;
  late TextEditingController whatsAppController;
  bool buttonEnabled = false;
  
  LibPhonenumberTextFormatter? phoneFormatter;

  @override void initState() {
    super.initState();
    User userInfo = ref.read(userInfoProvider);
    if (userInfo.phoneNumber != null) {
      updatePhoneFormat(userInfo.phoneNumber!);
    }
    fnameController = TextEditingController(text: userInfo.firstName);
    lnameController = TextEditingController(text: userInfo.lastName);
    emailController = TextEditingController(text: userInfo.email);
    phoneController = TextEditingController(text: userInfo.phoneNumber);
    discordController = TextEditingController(text: userInfo.discordID);
    whatsAppController = TextEditingController(text: userInfo.whatsAppID);
  }

  void canSubmit() {
    User userInfo = ref.read(userInfoProvider);
    if (_formkey.currentState!.validate()) {
      User currInfo = inputToUser();
      setState(() => buttonEnabled = userInfo != currInfo);
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

  User inputToUser() {
    User user = ref.read(userInfoProvider);
    return User(
      firstName: fnameController.text,
      lastName: lnameController.text,
      email: emailController.text,
      phoneNumber: phoneController.text.isEmpty ? null : phoneController.text,
      discordID: discordController.text.isEmpty ? null : discordController.text,
      whatsAppID: whatsAppController.text.isEmpty ? null : whatsAppController.text,
      appPreferences: user.appPreferences
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
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    User userInfo = ref.watch(userInfoProvider);
    var theme = Theme.of(context);

    List<Widget> textFields = [
      EditProfileTextField(
        name: 'First name',
        initValue: userInfo.firstName,
        keyboardType: TextInputType.name,
        controller: fnameController,
        onChange: (val) => canSubmit()
      ),
      EditProfileTextField(
        name: 'Last name',
        initValue: userInfo.lastName,
        keyboardType: TextInputType.name,
        controller: lnameController,
        onChange: (val) => canSubmit()
      ),
      EditProfileTextField(
        name: 'Email',
        initValue: userInfo.email,
        keyboardType: TextInputType.emailAddress,
        controller: emailController,
        onChange: (val) => canSubmit()
      ),
      EditProfileTextField(
        name: 'Phone number',
        initValue: userInfo.phoneNumber,
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
        initValue: userInfo.discordID,
        prefix: "@",
        optional: true,
        controller: discordController,
        onChange: (val) => canSubmit()
      ),
      EditProfileTextField(
        name: 'WhatsApp ID',
        initValue: userInfo.whatsAppID,
        optional: true,
        controller: whatsAppController,
        onChange: (val) => canSubmit()
      ),
    ];

    List<Widget> widgets = textFields;
    widgets.insert(0, Text(
      helpText
    ));

    widgets.add(
      TextButton(
        style: TextButton.styleFrom(
          backgroundColor: theme.colorScheme.primary,
          foregroundColor: theme.colorScheme.onPrimary,
          textStyle: TextStyle(fontWeight: FontWeight.bold)
        ),
        onPressed: buttonEnabled ?
          () {
            ref.read(userInfoProvider.notifier).update(inputToUser());            
            showTopSnackBar(
              Overlay.of(context),
              CustomSnackBar.success(
                backgroundColor: theme.dialogBackgroundColor,
                icon: Icon(Icons.abc, color: Colors.transparent),
                message: "Your profile has been successfully updated.",
                textStyle: TextStyle(color: theme.primaryColor),
              ),
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 40),
              reverseAnimationDuration: const Duration(milliseconds: 300),
              displayDuration: const Duration(milliseconds: 1600)
            );
            setState(() => buttonEnabled = false);
          }
          :
          null,
        child: const Text('Save Changes')
      )
    );
    
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
          'Edit Profile',
          style: TextStyle(color: theme.colorScheme.onSurface, fontWeight: FontWeight.w500))
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
            itemBuilder: (context, idx) => widgets[idx],
            separatorBuilder: (context, idx) => SizedBox(height: 30),
            itemCount: widgets.length)
        ),
      )
    );
  }
}