import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/pages/pages.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class SettingsPage extends ConsumerStatefulWidget {
  const SettingsPage({super.key});

  @override
  SettingsPageState createState() => SettingsPageState();
}

class SettingsPageState extends ConsumerState<SettingsPage> {
  var selected = false;
  
  @override
  Widget build(BuildContext context) {
    User user = ref.watch(userInfoProvider);
    Widget divider = Divider(indent: 20, endIndent: 20, height: 0);
    var theme = Theme.of(context);

    return Scaffold(
      body: Stack(
        children: [
          Container(height: double.infinity),
          Positioned(
            child: FractionallySizedBox(
              heightFactor: 0.45,
              widthFactor: 1.0,
              child: Container(
                decoration: BoxDecoration(
                  color: theme.colorScheme.primary,
                  borderRadius: BorderRadius.only(
                    bottomLeft: const Radius.circular(30),
                    bottomRight: const Radius.circular(30)
                  )
                ),
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    children: [
                      SizedBox(height: 20),
                      ListTile(
                        leading: Icon(Icons.settings, size: 30),
                        title: Text('Settings'),
                        iconColor: theme.colorScheme.onPrimary,
                        titleTextStyle: TextStyle(
                          color: theme.colorScheme.onPrimary,
                          fontSize: 30,
                          fontWeight: FontWeight.bold
                        ),
                      )
                    ],
                  ),
                )
              )
            )
          ),
          Positioned(
            top: 100,
            left: 0,
            right: 0,
            bottom: 0,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Container(
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainer,
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(30),
                    topRight: const Radius.circular(30)
                  )
                ),
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          SectionHeading(heading: '${user.firstName} ${user.lastName}'),
                          Padding(
                            padding: const EdgeInsets.all(4.0),
                            child: Text(
                              user.email,
                              style: TextStyle(
                                fontSize: 16
                              ),
                            )
                          )
                        ],
                      ),
                    ),
                    Divider(),
                    SizedBox(height: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        FullWidthButton(
                          title: 'Edit Profile',
                          leading: Icon(Icons.person),
                          trailing: Icon(Icons.arrow_forward),
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (context) => EditProfilePage()
                              )
                            );
                          }
                        ),
                        divider,
                        FullWidthButton(
                          title: 'Appearance',
                          leading: Icon(Icons.palette),
                          trailing: Icon(Icons.arrow_forward),
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (context) => AppearancePage()
                              )
                            );
                          }
                        ),
                        divider,
                        FullWidthButton(
                          title: 'Manage History',
                          leading: Icon(Icons.history),
                          trailing: Icon(Icons.arrow_forward),
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (context) => ManageHistoryPage()
                              )
                            );
                          }
                        ),
                        divider,
                        FullWidthButton(
                          title: 'About',
                          leading: Icon(Icons.info),
                          trailing: Icon(Icons.arrow_forward),
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (context) => AboutPage()
                              )
                            );
                          }
                        ),
                      ],
                    )
                  ],
                )
              ),
            ),
          )
        ],
      )
    );
  }
}