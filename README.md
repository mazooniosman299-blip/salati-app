# صلاتي — مصدر الحالة الحالي

> آخر فحص هندسي: 5 نوفمبر 2026. إصدار هذا الفرع **1.0.132 / Android code132**؛ المصدر `apk-release-parts/current.json`. فُحصت الصلوات الخمس في محاكي أندرويد مع إغلاق التطبيق والشاشة، والأيقونة هي المسجد الملوّن المختار. آخر إنتاج متحقق قبل هذا الفرع1.0.130؛ حالة النشر والتحقق العام موثقة في [PR53](https://github.com/mazooniosman299-blip/salati-app/pull/53) بعد اجتياز بوابات النشر، ولا يُستنتج النشر من وجود APK وحده.

الموقع الرسمي: https://salati-app-ctc.pages.dev/. أي تغيير في أصول الويب يتطلب إثبات تطابق بصمة الموقع مع ملف APK الموقّع بالشهادة الأصلية قبل النشر. مشروع صلاتي بواجهة داكنة وبستة تبويبات، وملفات المصحف والبيانات الصوتية والويجت الأصلية محمية من التعديل غير المطلوب.

## نقطة البداية لكل طلب ChatGPT
اقرأ [AGENTS.md](AGENTS.md)، [المواصفات الحالية](docs/CURRENT_APPROVED_DESIGN.md)، [خريطة مصادر التنفيذ](docs/ACTUAL_SOURCE_MAP.md)، [تعارض التعليمات](docs/INSTRUCTION_CONFLICTS.md)، [سجل المخاطر العشرين](docs/ROOT_CAUSE_AUDIT_20261103.md)، و[سجل طلب التعديل الحالي](docs/requests/ACTIVE_CHANGE.json). لا تعتبر صور المعاينة أو الاختبارات القديمة بديلاً عن آخر تعليمات المستخدم.

## تشغيل الفحوص
```sh
npm ci
npm run build
npm test
node tests/permanent-regression-contract.cjs
node tests/agent-governance-contract.cjs
node scripts/inventory-current-sources.cjs
node tests/reference-provenance.cjs
```

الاختبار المتصفح الحقيقي مع Playwright: `python3 tests/current-design-visual-proof.py`. حماية نطاق الملفات: `node scripts/verify-change-scope.cjs origin/production`. استخدم مسودة PR ونتائج CI، ولا تدمج الفرع أو تنشر قبل التوقيع ونتيجة الاختبار المعتمدة.

## الأرشيف
المستند القديم الذي وصف 1.0.116 بالإصدار المنشور محفوظ كاملًا في [docs/archive/README-LEGACY-20261101.md](docs/archive/README-LEGACY-20261101.md)، ولا يُستخدم كمصدر نشط للنسخة الحالية.

**حدود هذه المراجعة:** لا تثبت مطابقة أي صورة أخيرة غير متاحة ولا تثبت الاختبار على هاتف فعلي. المصحف والمشغل ما زالا بحاجة لمطابقة آخر مرجع.
