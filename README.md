# RePlex Notifier

A basic python script to send a notification via PushBullet when someone starts or stops watching media on your Plex server _(this can be configured)_.

PushBullet Notification for play activity:

```
Replex - Activity
<User> started playing ... on <Client>
```

PushBullet Notification for stop activity:

```
Replex - Activity
<User> stopped ... on <Client>
```

### Setup

Edit the `config.json` file with your Plex `serverIp` and `pushbulletAccessToken`.

### Usage

Run the script on your Plex server (preferred) or another server residing on your network.

**Nix:** `python replexNotifier.py` or run it in the background, `python replexNotifier.py &`

**Windows:** Download the `replexNotifier_v0.1_win32.zip` Windows executable from the releases page and double-click to execute.
