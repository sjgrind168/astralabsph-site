# AstraLabs PH / Marketing Automation

**Campaign:** Astramate 2.0 and Keepry Android launch, worldwide English. PIREVO is separate.

## The single publishing folder

- `marketing/automation/facebook/scripts/` stores the Facebook queue program and approved text bank. Visual assets are mirrored publicly under `public/marketing/campaigns/facebook/` after a one-time owner-approved upload.
- `marketing/automation/pinterest/scripts/` stores the Pinterest queue program and approved Pin bank. Public creative assets: `public/marketing/pins/` (legacy) and `public/marketing/campaigns/pinterest/` (new campaign).
- `marketing/automation/tiktok/scripts/` stores TikTok queue program and approved MP4 references. Public MP4 assets: `public/marketing/videos/` **not uploaded yet**.
- Owner's original media library (including the current two MP4s, 16 campaign PNGs, captions and Mac upload helper): `/AstraLabs PH/Marketing Automation/AstraLabs_Marketing_Automation_Folder_20260922.zip` in ChatGPT Library. It has `facebook/`, `pinterest/`, `tiktok/`, `youtube/`, `shared/` and `website_upload/` subfolders.
- The chat Library is PRIVATE. Buffer cannot read those links; it must use tested public `https://www.astralabsph.com/marketing/...` assets before any unattended media publishing.

## Existing workflow safety

The existing Facebook, Pinterest and TikTok workflows are live in `.github/workflows/`. Their main programs are still the old `marketing/buffer_*.py` files; the copies here are **staged** until the workflows are deliberately switched over in a controlled, tested change. Do not run both old and new queues at once.

Facebook has a 10-item preapproved **text** bank and refills up to 5; Pinterest is capped at 1 while the new dedicated board and first image publishing proof are reconciled. TikTok uses read-only preflight: the API verifies @astralabsph and reports MEDIA_NOT_HOSTED for the missing direct MP4 URL. NO TikTok post has been scheduled by the GitHub automation yet.

## Steps to finish full auto-publishing

1. Unzip the owner's media pack on the Mac, inspect source app screenshots for sensitive details, and run `publish_approved_media_to_github.command` only after the owner confirms the intended promotional assets may be public. This action commits only two MP4 ads and 16 campaign PNGs to the existing website repository; no Library or original app source is modified.
2. Verify public HTTPS MP4 and PNG responses, real content types and full video playback after Vercel deploy.
3. Verify TikTok MP4 API metadata against current Buffer docs and do exactly ONE scheduled TikTok post, then verify the live @astralabsph profile and caption. Only then increase the queue limit and enable writes.
4. Reconcile current Facebook/Pinterest scheduled+sent queues before replacing old text/typography creatives with the new 4:5/2:3 image posts. Require exact campaign markers and no double-posting.
5. YouTube stays separate: the free Buffer account has three channels. Use YouTube Studio scheduling initially; API publishing needs owner Google authorization and public upload eligibility verification.

No tokens, passwords, or personal paperwork should be committed into this public repository.
