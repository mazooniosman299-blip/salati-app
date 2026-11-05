# صلاتي — مصدر الحالة الحالي

> آخر فحص هندسي: 5 نوفمبر 2026. هذا الفرع مرشح **1.0.131 / Android code132** لإصلاح فقدان منبّه الصلاة أثناء إعادة حفظ الجدول وتطبيق أيقونة المسجد الملوّنة المختارة. أساسه الإنتاج المتحقق `production@38c5989`، الإصدار الرسمي1.0.130. النشر131 ينتظر الفحوص والتحديث الموقّع والتحقق العام؛ وجود الملف المرشح لا يثبت النشر.

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
