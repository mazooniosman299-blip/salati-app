# Runtime-triggered visual differential safety

When HTML, canonical CSS or Quran/application renderer source changes, CI must capture and compare **both** the current production app and the candidate using real Chromium. This rule is based on the actual Git diff, not on an editable JSON boolean.

For a request marked `visual_change: true`, a nonempty `visual_allowed_regions` lists precise tab, language and DOM selector (e.g. `{"tab":"mushaf","language":"both","selector":"#qTransport"}`). The pixel comparator rejects differences outside these selected bounding boxes and requires at least one changed pixel inside.

For a request marked `visual_change: false`, no visual region is allowed and CI fails if rendered screenshots differ more than the tiny per-frame noise budget. This protects unrelated components when behavior code changes.

Native Android widget/release testing is separate. This comparator does **not** certify exact identity to the user's last original screenshot, which remains governed by the reference registry.
