# Subtitle Player (Android)

A [Capacitor](https://capacitorjs.com/) wrapper that packages the
[Subtitle Player](https://spencerlee.net/subtitle-player/) web app as a native
Android app. The web code runs in a WebView and is bundled inside the app, so
the installed app is fully self-contained and works with no network and no
hosted URL.

- **App ID:** `net.spencerlee.subtitleplayer`
- **Web source:** the sibling `../subtitle-player` repo (single source of truth)

## Layout

- `www/` -- the bundled web app, copied from `../subtitle-player`.
- `scripts/sync-web.mjs` -- copies the web files into `www/`.
- `scripts/gen-native-icons.py` -- draws the launcher icon and splash layers
  into `assets/` (needs Python + Pillow).
- `assets/` -- icon/splash sources for `@capacitor/assets`.
- `android/` -- the generated native Gradle project.

## Prerequisites

- Node 18+ and npm (`npm install` to restore dependencies).
- A JDK (17 recommended) and the Android SDK.
- Gradle is provided by the wrapper; no system Gradle needed.

## Update the bundled web app

After changing `../subtitle-player`:

```sh
npm run sync        # copy www/ from the web repo, then `cap sync android`
```

## Regenerate the launcher icon / splash

```sh
python3 scripts/gen-native-icons.py
npx @capacitor/assets generate --android
```

## Build a debug APK

```sh
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64   # a JDK 17
export ANDROID_HOME="$HOME/Android/Sdk"
cd android && ./gradlew assembleDebug
```

The APK lands at `android/app/build/outputs/apk/debug/app-debug.apk` and can be
sideloaded (`adb install`) directly.

## Build a signed release

Release signing reads `android/app/keystore.properties`, which points at an
upload keystore. Both files are gitignored and must be kept private and backed
up. `keystore.properties` looks like:

```properties
storeFile=upload-keystore.jks
storePassword=…
keyAlias=upload
keyPassword=…
```

Then:

```sh
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export ANDROID_HOME="$HOME/Android/Sdk"
cd android && ./gradlew bundleRelease   # -> app/build/outputs/bundle/release/app-release.aab (Play upload)
./gradlew assembleRelease               # -> app/build/outputs/apk/release/app-release.apk (sideload)
```

The `.aab` is what Google Play wants. This project uses Play App Signing, so the
keystore above is the *upload* key (resettable via Play if lost); Google holds
the actual app-signing key. Bump `versionCode` in `app/build.gradle` for each
Play upload.

## License

AGPL-3.0-or-later, matching the bundled web app. See `LICENSE.txt`.
