# Publishing Notes

## Whitelisted Server

WeChat official account API calls must originate from an IP in the account whitelist. If the whitelist is `<YOUR_SERVER_IP>`, run `wechat_add_draft.py` or `wechat_update_draft.py` on that server, not on the local Mac.

Recommended pattern:

```bash
scp article.json thumb.jpg body-image.png scripts/wechat_add_draft.py root@<YOUR_SERVER_IP>:/root/wechat_publish/
ssh root@<YOUR_SERVER_IP> 'cd /root/wechat_publish && set -a && . ./wechat.env && set +a && python3 wechat_add_draft.py --article article.json --thumb thumb.jpg --content-image body-image.png'
```

Never include real `wechat.env`, SSH keys, AppSecret, or access tokens in the skill zip.

## Cover Standard

The cover should feel like a premium business magazine, not a cheap training poster.

Use imagegen for:

- no-text premium background
- dark business/AI atmosphere
- abstract dashboards, glass panels, cost curves, workflow nodes

Use local compositing for:

- exact Chinese title
- Yuan Liuwei real portrait
- crop parameters and thumbnail

Avoid:

- thick gold outline text
- sticker badges
- fake Chinese text
- AI-redrawn faces
- floating cutout head
- crowded cyberpunk UI

## Public-Safe Rules

For public articles:

- verify external source facts
- preserve original internal notes separately
- avoid unsupported income claims
- avoid official affiliation claims unless verified
- avoid customer/student privacy exposure
- write "can inspire" instead of "guarantees"
