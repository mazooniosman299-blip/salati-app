# استعادة مفتاح توقيع صلاتي واستخدامه على جهاز آخر

هذا مفتاح الإصدار الثابت الذي أُنشئ بإذن صاحب التطبيق في 23 أكتوبر 2026. استخدم المفتاح نفسه لجميع التحديثات التالية. لا تنشئ بديلًا عند فقدانه؛ استعد النسخة الاحتياطية.

| الإعداد العام | القيمة |
| --- | --- |
| معرّف التطبيق | `com.salati.prayer` |
| الاسم المستعار | `salati` |
| نوع المخزن | `PKCS12` |
| أول إصدار بهذا التوقيع | `1.0.68`، رقم البناء `69` |
| SHA-256 للشهادة | `559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e` |

**الإصدار 1.0.67 يحمل توقيعًا مختلفًا.** يتطلب الانتقال منه إلى 1.0.68 بالتوقيع الجديد إزالة النسخة القديمة، مما قد يمسح بياناتها المحلية. أما تحديثات 1.0.68 وما بعده فتستخدم هذا المفتاح الثابت ومعرّف التطبيق نفسه ورقم بناء أعلى.

## الملفات التي يجب تنزيلها والاحتفاظ بها

1. حزمة `salati-signing-recovery-kit-2026-10-23.zip` من مجلد Drive الخاص. بداخلها ملف النسخة المشفّرة وأداة استعادة تعمل محليًا دون اتصال.
2. ملف `SALATI-RECOVERY-SECRET-PRIVATE.txt` الخاص المنفصل. يحتوي رمز فتح الحزمة؛ احفظه في مدير كلمات مرور أو مكان خاص مستقل.
3. نسخة من مصدر المشروع. الحزمة المستعادة تتضمن أيضًا أدوات التوقيع وبيانات الهوية العامة، لتعمل حتى بعد حذف مشروع Codex.

لا تنشر هذه الملفات في GitHub أو موقع التنزيل. لا ترسل كلمة المرور في سجل بناء أو سطر أوامر. الحزمة المشفّرة تستخدم AES-256-GCM مع PBKDF2-HMAC-SHA256 و600,000 دورة وملح عشوائي. ملف الاسترداد الخاص لا يدخل الحزمة العامة أو Git.

## الاستعادة دون Codex

1. فك ضغط حزمة الاسترداد على جهازك.
2. افتح `restore-salati.html` في Chrome أو Edge أو Firefox حديث. اختر ملف `salati-signing-backup.salati-backup` من الحزمة وأدخل رمز الاسترداد من الملف الخاص المنفصل.
3. نزّل ZIP المستعاد الذي تنتجه الصفحة. تعمل العملية محليًا؛ لا تتصل الصفحة بخادم ولا ترسل المفتاح أو كلمة المرور.
4. فك ZIP المستعاد في مجلد خاص. ستجد `signing.keystore` الأصلي، و`keystore-password.txt`، و`android/signing-identity.json`، وأدوات التوقيع، وهذه التعليمات.
5. على Linux وmacOS وWSL، احمِ الملفات قبل استخدامها:

```bash
chmod 700 /private/path/salati-signing
chmod 600 /private/path/salati-signing/signing.keystore /private/path/salati-signing/keystore-password.txt
```

المفتاح وكلمة مروره موجودان داخل النسخة المشفّرة، ورمز فتحها في الملف الخاص المنفصل. لن تحتاج إلى محادثة Codex أو بيئته لاستعادتهما.

## بناء تحديث وتوقيعه

ثبّت Python 3.9+ وJDK 17+ وأدوات Android SDK المناسبة للمشروع. على Windows يمكن استخدام WSL أو تشغيل أداة Python بالأدوات المناسبة للنظام.

عيّن مسارات الملفات الخاصة فقط؛ لا تضع كلمة المرور نفسها في الأوامر:

```bash
export JAVA_HOME="/path/to/jdk"
export ANDROID_BUILD_TOOLS="/path/to/android-sdk/build-tools/36.0.0"
export SALATI_KEYSTORE="/private/path/salati-signing/signing.keystore"
export SALATI_PASSWORD_FILE="/private/path/salati-signing/keystore-password.txt"
```

تحقق من المفتاح أولًا:

```bash
python3 scripts/sign-android.py --check-key
```

يجب أن ينجح فحص البصمة والاسم `salati`. سيُرفض ملف مفقود أو كلمة مرور غير صحيحة أو بصمة مختلفة، ولن يُنشأ مفتاح جديد. يحوي المصدر فحص Gradle إلزاميًا قبل `preReleaseBuild` يطبق الشرط نفسه. لا تغيّر `android/signing-identity.json` لتجاوز خطأ البصمة.

ارفع `versionCode` فوق أعلى نسخة مثبّتة، مع بقاء `applicationId` كما هو. مثال لتحديث لاحق:

```bash
cd android
./gradlew :app:assembleRelease -PsalatiVersionCode=70 -PsalatiVersionName=1.0.69
cd ..
python3 scripts/sign-android.py --input android/app/build/outputs/apk/release/app-release-unsigned.apk --output salati-1.0.69.apk
```

إذا استخدمت أداة التوقيع من الحزمة المستعادة بدل المصدر، استعمل `python3 tools/sign-android.py --input /path/update-unsigned.apk --output /path/update-signed.apk`؛ بيانات الهوية موجودة في `android/signing-identity.json` داخل الحزمة.

أداة التوقيع تتحقق من شهادة المفتاح قبل العمل، ومن معرّف التطبيق قبل التوقيع، ثم من توقيع APK وبصمة الشهادة ومعرّف التطبيق ورقم الإصدار والمحاذاة بعد التوقيع. تُعرض البيانات العامة فقط، ولا تُطبع كلمات المرور. النسخ الاحتياطية والملفات الخاصة تبقى خارج المستودع.
