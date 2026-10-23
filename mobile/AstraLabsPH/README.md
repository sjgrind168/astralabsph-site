# AstraLabs PH · Native iPhone owner app (SwiftUI)

## Product, not a website wrapper
This is the actual native SwiftUI source foundation for the owner's unified AstraLabs PH app. The current /command-center/mission-preview/ website route is solely for rapid UI review, not the final app runtime.

### Five tabs
1. Home: Apple developer proceeds, KDP royalty estimates, source freshness, priority tasks and a short AKAME insight.
2. Analytics: revenue streams separately, app performance, KDP books and dated social snapshots. Never combine gross sales, payouts and proceeds.
3. AKAME: dedicated AI chat tab, eventually backed by a private cloud inference service. Mac-local coding and Hindsight memory remain separate until safely synced.
4. Tasks: pending, owner approvals and completed work with receipts. ASTRA/AKAME coordination appears inside mission threads, not a separate tab.
5. More: security, model route health, integrations, notifications, full Akashic archive link.

## Current implementation status
- SwiftUI source and XcodeGen target configured; iPhone-only iOS 18+.
- A read-only astralabs-mobile-summary Supabase Edge endpoint is deployed. It accepts authenticated owner passkey sessions, not anonymous users or agent tokens. Unauthorized request tested 401, POST 405; owner authorized path requires QA.
- Existing astralabs-akashic?view=dashboard endpoint supplies tasks/projects after owner passkey auth.
- Existing passkey Edge endpoint only accepts web origin https://www.astralabsph.com and RP ID www.astralabsph.com. Native iOS AuthenticationServices requires associated-domain setup and explicit iOS-origin verification. Do not bypass authentication or embed session tokens.
- App shows real private business data only after a valid native session. Until then it displays unavailable states. Chat send and executor approvals are not yet enabled.
- With Mac offline, cloud AI can eventually analyze reports and create missions but cannot use Mac-only browser, Xcode or local Hindsight memory.
- ASTRA cannot automatically answer just because a record is saved. Requires supported scheduled agent runner or authenticated cloud agent distinct from ordinary ChatGPT conversation.

## Release gates
1. Approve native five-tab UI, black/white typography and straightforward metrics.
2. Implement and test native iOS passkey with Apple App Site Association, dedicated entitlement and correct iOS-origin verification, preserving website WebAuthn.
3. Certify provider freshness. Apple, KDP, Google Play and AdMob have different reporting periods; GA4 property not confirmed.
4. Implement owner-approved mission/event/lease queue and idempotent worker execution, including Mac offline semantics.
5. Add allowed free-model router, strict zero-spend enforcement, real provider cooldowns and authenticated cloud memories.
6. Recover disk space safely before Xcode build. Preserve Shoku Build24, historic fixtures, Mac AKAME data and simulator files.

## Local development
Run from mobile/AstraLabsPH: xcodegen generate; open AstraLabsPH.xcodeproj.
Do not describe the app as installed or production-capable until signing/device QA passes.