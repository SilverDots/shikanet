import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_libphonenumber/flutter_libphonenumber.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/utils/utils.dart';

part 'user_info_provider.g.dart';

@Riverpod(keepAlive: true)
class UserInfo extends _$UserInfo {
  @override
  User build() {
    return User(
      firstName: "Kasten",
      lastName: "Welsh",
      email: 'user@gmail.com',
      phoneNumber: formatNumberSync(
        '101-202-3003',
        country: CountryWithPhoneCode.us(),
        inputContainsCountryCode: false,
        phoneNumberFormat: PhoneNumberFormat.national
      ),
      discordID: 'dunsparse0p',
      appPreferences: defaultPreferences
    );
  }

  void update(User u) {
    state = u;
  }
}