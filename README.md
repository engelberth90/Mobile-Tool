Welcome to Mobile Tool!

Mobile Tool is a tool designed to automate the configuration of Android mobile devices for security audits. Additionally, functions that are highly useful during audits are being implemented, with plans for continued growth.

Currently, Mobile Tool is only compatible with Windows. A new version is being developed to also support Linux.

## How to use Mobile Tool
1. Install all the requirements with the following command:
```python
pip install -r requirements.txt
```
2. After the installation, simply run the following command:
```python
python MobileT.py
```
```python
     __  __       _       _     _____
    |  \/  | ___ | |__ (_) | __|_   _|
    | |\/| |/ _ \| '_ \| | |/ _ \| |
    | |  | | (_) | |_) | | |  __/| |
    |_|  |_|\___/|_.__/|_|_|\___||_|

                By: T1N0
                
    MENU:

  1. Android Device Configuration.
  2. Static Analysis of APK.
  3. Detect Application Technology.
  4. Exit.

  Select an option (1-4):
```



# Features

1. Android Device Configuration.
     1.1 Insert Burp Suite certificate.
     1.2 Insert frida server and client.
2. Static Analysis of APK.
3. Detect Application Technology.

## Android Device Configuration

### Insert Burp Suite certificate
We have two options: configuring a mobile device to install the Burp Suite certificate at the system level, and downloading the Frida server compatible with the device's architecture.

We'll start by configuring the device with the Burp Suite certificate:

1. Launch Burp Suite, set the IP address provided by the Wi-Fi network, and configure a port of your choice, for example:
```
IP: 192.168.0.12
Port: 8080
```
2. When we choose option A, which is the configuration to insert the Burp Suite certificate, the tool will ask for the IP address and port configured in Burp Suite, and we will need to assign them.
```python
Android Device Settings:

  A. Insert Burp Suite certificate.
  B. Insert frida server and client.

  Select an option (A/B): A

  Enter the Burp Suite IP address: 192.168.0.12
  Enter Burp Suite port: 8080
```
After setting the IP address and port, we press enter, and the tool will automatically handle downloading the Burp Suite certificate, converting it, pushing it to the device, and placing it in the certificates directory to be recognized as a trusted certificate.
```python
  Enter the Burp Suite IP address: 192.168.0.12
  Enter Burp Suite port: 8080

  [+]    Burp Suite certificate downloaded successfully.
  [+]    Certificate converted to PEM successfully.
  [+]    PEM certificate sent to /sdcard/ successfully using ADB.
  [+]    File system remounted successfully using ADB.
  [+]    File moved to /system/etc/security/cacerts/ successfully using ADB.
  [+]    File permissions changed correctly using ADB.
  [+]    The device will reboot.
  [+]    Temporary files deleted successfully.
```
At this point, the device will restart, but it is recommended to power it off and then turn it back on.

If we then check the user-level certificates, we will see the `portswigger` certificate.

### Insert frida server and client
When selecting the option 'B. Insert Frida server and client,' the tool will automatically identify the device's architecture and download the compatible version of the Frida server. It will then send the file to the device's internal path '/data/local/tmp' with the necessary permissions to use the binary when needed, and install the compatible version of the Frida client on the Windows host.
```python
Android Device Settings:

  A. Insert Burp Suite certificate.
  B. Insert frida server and client.

  Select an option (A/B): B

  [+]    Device architecture detected: x86_64
  [+]    frida-server version 16.3.3, successfully downloaded for x86_64.
  [+]    frida-server unzipped correctly.
  [+]    frida-server transferred to device at /data/local/tmp.
  [+]    Permissions successfully granted to the frida-server file on the device.
  [+]    Temporary files deleted successfully.
  [+]    Installing frida-tools and frida client version 16.3.3...
  [+]    frida-tools installed correctly.
  [+]    frida client version 16.3.3 installed correctly.
```
If we now check the file in the path '/data/local/tmp', we will find the Frida binary with the necessary permissions.
```bash
d2q:/data/local/tmp # ls -l
total 110716
-rwxrwxrwx 1 root root 113371768 2024-09-17 01:00 frida-server
d2q:/data/local/tmp #
```
To check the compatibility between the Frida server binary and the Frida client we installed on Windows, we will list the processes using Frida.

Frida Server
```bash
d2q:/data/local/tmp # ./frida-server &
[1] 3522
d2q:/data/local/tmp #
```
Frida Client
```bash
PS C:\Users\T1N0> frida-ps -U
 PID  Name
----  ----------------------------------------------
3171  Facebook
1580  adbd
2155  android.ext.services
1555  android.hardware.audio@2.0-service
1556  android.hardware.bluetooth@1.0-service.btlinux
2353  android.hardware.camera.provider@2.4-service
1558  android.hardware.cas@1.0-service
1559  android.hardware.configstore@1.1-service
1560  android.hardware.dumpstate@1.0-service
1561  android.hardware.light@2.0-service
1562  android.hardware.memtrack@1.0-service
1563  android.hardware.power@1.0-service
1564  android.hardware.usb@1.0-service
1565  android.hardware.wifi@1.0-service
1553  android.hidl.allocator@1.0-service
1569  audioserver
1584  cameraserver
2628  com.android.inputmethod.pinyin
2315  com.android.launcher3
2074  com.android.phone
1884  com.android.systemui
2615  com.google.android.gms
2409  com.google.android.gms.persistent
3356  com.google.android.gms.unstable
2734  com.google.android.webview:sandboxed_process0
3376  com.google.process.gapps
1585  drmserver
```
Now we can confirm that everything has been installed correctly.

## Static Analysis of APK
When selecting the option '2. Static Analysis of APK or IPA,' the tool will prompt us for the path of the APK file we want to perform the static analysis on. At this point, 'apkleaks' is used, so full credit goes to its creators.
```python
 Select an option (1-4): 2

  Enter the path of the APK or IPA file for static analysis: C:\Users\T1N0\Downloads\com.conferenciagt.pwn3d.apk
  Starting static analysis with apkleaks...
  Analysis completed successfully. Results:

INFO  - loading ...
INFO  - processing ...
INFO  - done
** Decompiling APK...

** Scanning against 'com.conferenciagt.pwn3d'

[JSON_Web_Token]
- androidGradlePluginVersion=7.3.1

[LinkFinder]
- /proc/self/fd/
- activity_choser_model_history.xml
- http://schemas.android.com/apk/res/android
- share_history.xml
```
The results may vary significantly, so it is recommended to carefully review them and perform a manual static analysis of the strings obtained by the tool.

## Detect Application Technology.
When selecting the option '3. Detect Application Technology,' the tool will analyze the technologies used by the application to determine if it is native or hybrid. This step is crucial in the enumeration phase of our penetration tests, as it provides insight into how to approach the challenge. Additionally, if it detects that the application is built with Flutter, the tool uses ReFlutter to patch the app and enable request interception.

```python
Select an option (1-4): 3

  Enter the path to the APK or IPA file: C:\Users\T1N0\Descargas\Base.apk

 [+]Application : Híbrida

 [+] Technologies detected: React Native
```
Happy Hacking!
