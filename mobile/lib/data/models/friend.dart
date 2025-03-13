class Friend {
  Friend({
    required this.firstName,
    this.lastName,
    this.email,
    this.phoneNumber,
    this.discordID,
    this.whatsAppID,
    this.notes = ""
  });

  final String firstName;
  final String? lastName;
  final String? email;
  final String? phoneNumber;
  final String? discordID;
  final String? whatsAppID;
  final String notes;

  Friend copyWith({
    final String? firstName,
    final String? lastName,
    final String? email,
    final String? phoneNumber,
    final String? discordID,
    final String? whatsAppID,
    final String? notes
  }) {
    return Friend(
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      email: email ?? this.email,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      discordID: discordID ?? this.discordID,
      whatsAppID: whatsAppID ?? this.whatsAppID,
      notes: notes ?? this.notes
    );
  }

  @override
  int get hashCode {
    int val = super.hashCode;
    val = 31 * val + firstName.hashCode;
    val = 31 * val + notes.hashCode;
    if (lastName != null) {
      val = 31 * val + lastName.hashCode;
    }
    if (email != null) {
      val = 31 * val + email.hashCode;
    }
    if (phoneNumber != null) {
      val = 31 * val + phoneNumber.hashCode;
    }
    if (discordID != null) {
      val = 31 * val + discordID.hashCode;
    }
    if (whatsAppID != null) {
      val = 31 * val + whatsAppID.hashCode;
    }
    return val;
  }

  @override
  bool operator ==(Object other) {
    if (other is Friend
        && firstName == other.firstName
        && lastName == other.lastName
        && email == other.email
        && phoneNumber == other.phoneNumber
        && discordID == other.discordID
        && whatsAppID == other.whatsAppID
        && notes == other.notes) {
      return true;
    }
    return false;
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> res = {'firstName': firstName};
    if (lastName != null) {
      res['lastName'] = lastName;
    }
    if (email != null) {
      res['email'] = email;
    }
    if (phoneNumber != null) {
      res['phone'] = phoneNumber;
    }
    if (discordID != null) {
      res['discordID'] = discordID;
    }
    if (whatsAppID != null) {
      res['whatsAppID'] = whatsAppID;
    }
    res['notes'] = notes;
    return res;
  }
}