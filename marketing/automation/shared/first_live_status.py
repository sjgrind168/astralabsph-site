# AstraLabs first live-post read-only recheck after TikTok media processing.
#!/usr/bin/env python3
import importlib.util,json
from pathlib import Path
p=Path('marketing/automation/tiktok/scripts/buffer_tiktok.py')
spec=importlib.util.spec_from_file_location('tt',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
org,ch=m.resolve_tiktok()
for kind,pid in [('TIKTOK_V2_ORIGINAL_ERROR','6ab1f12dffe5c8afb1291a9b'),('TIKTOK_V2_30FPS','6ab1f25574424003bca6ed63'),('FACEBOOK_VISUAL','6ab1f12a6ed20e9354f5cfba')]:
    q='query { post(input:{id:'+json.dumps(pid)+'}) { id channelId status externalLink sharedNow error { message supportUrl } assets { mimeType source } } }'
    result=m.gql(q).get('post') or {}
    if result.get('id')!=pid:raise RuntimeError(kind+' exact post missing')
    print('POST_DIAG',kind,'status',result.get('status'),'externalLink',result.get('externalLink'),'sharedNow',result.get('sharedNow'),'error',json.dumps(result.get('error'),ensure_ascii=True),'media_count',len(result.get('assets') or []))
