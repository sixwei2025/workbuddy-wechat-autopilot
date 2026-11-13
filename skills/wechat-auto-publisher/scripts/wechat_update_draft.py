#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import mimetypes
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.weixin.qq.com/cgi-bin"


def request_json(url, data=None, headers=None):
    body = None
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            headers = {"Content-Type": "application/json", **(headers or {})}
        else:
            body = data
    req = urllib.request.Request(url, data=body, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("errcode"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))
    return payload


def get_access_token(appid, secret):
    return request_json(
        f"{API}/stable_token",
        {
            "grant_type": "client_credential",
            "appid": appid,
            "secret": secret,
            "force_refresh": False,
        },
    )["access_token"]


def multipart_file(field_name, file_path):
    path = Path(file_path)
    boundary = "----codexwechatupdateboundary"
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    chunks = [
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{path.name}"\r\n'.encode(),
        f"Content-Type: {mime}\r\n\r\n".encode(),
        path.read_bytes(),
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return boundary, b"".join(chunks)


def upload_thumb(access_token, thumb_path):
    boundary, body = multipart_file("media", thumb_path)
    query = urllib.parse.urlencode({"access_token": access_token, "type": "thumb"})
    return request_json(
        f"{API}/material/add_material?{query}",
        body,
        {"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )["media_id"]


def upload_image(access_token, image_path):
    boundary, body = multipart_file("media", image_path)
    query = urllib.parse.urlencode({"access_token": access_token})
    return request_json(
        f"{API}/media/uploadimg?{query}",
        body,
        {"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )["url"]


def update_draft(access_token, media_id, article_path, thumb_media_id):
    article = json.loads(Path(article_path).read_text(encoding="utf-8"))
    article["thumb_media_id"] = thumb_media_id
    article["pic_crop_235_1"] = "0_0_1_1"
    article["pic_crop_1_1"] = "0.287_0_0.713_1"
    query = urllib.parse.urlencode({"access_token": access_token})
    return request_json(
        f"{API}/draft/update?{query}",
        {"media_id": media_id, "index": 0, "articles": article},
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-id", required=True)
    parser.add_argument("--article", required=True)
    parser.add_argument("--thumb", required=True)
    parser.add_argument("--content-image", action="append", default=[])
    parser.add_argument("--max-paragraph", type=int, default=80)
    parser.add_argument("--min-images", type=int)
    parser.add_argument("--no-require-xiaohei", action="store_true")
    args = parser.parse_args()

    appid = os.environ["WECHAT_APP_ID"]
    secret = os.environ["WECHAT_APP_SECRET"]
    validation_args = ["--article", args.article, "--max-paragraph", str(args.max_paragraph)]
    if args.min_images is not None:
        validation_args.extend(["--min-images", str(args.min_images)])
    if args.no_require_xiaohei:
        validation_args.append("--no-require-xiaohei")
    subprocess.run([sys.executable, str(Path(__file__).with_name("validate_wechat_article.py")), *validation_args], check=True, stdout=sys.stderr)
    token = get_access_token(appid, secret)
    replacements = {}
    for image_path in args.content_image:
        path = Path(image_path)
        replacements[path.name] = upload_image(token, image_path)

    if replacements:
        article_path = Path(args.article)
        article = json.loads(article_path.read_text(encoding="utf-8"))
        content = article.get("content", "")
        for name, url in replacements.items():
            content = content.replace(f'src="{name}"', f'src="{url}"')
            content = content.replace(f'src="assets/{name}"', f'src="{url}"')
            content = content.replace(f'src="./assets/{name}"', f'src="{url}"')
        article["content"] = content
        article_path.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")

    thumb_media_id = upload_thumb(token, args.thumb)
    update_draft(token, args.media_id, args.article, thumb_media_id)
    print(json.dumps({"ok": True, "media_id": args.media_id, "thumb_media_id": thumb_media_id}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
