import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_libphonenumber/flutter_libphonenumber.dart';

part 'phone_formatter.g.dart';

@riverpod
Future<Map<String, CountryWithPhoneCode>> phoneFormatter(Ref ref) async {
  var map = await getAllSupportedRegions();
  return map;
}