"""유튜브 자동 업로드용 refresh token 을 내 PC 에서 한 번 받는다 (채널마다 한 번).

    YT_CLIENT_ID=... YT_CLIENT_SECRET=... python -m tools.auth_youtube

1. 브라우저가 열리면 **그 채널의 구글 계정**으로 로그인하고 권한을 허용한다.
2. 화면에 나온 refresh token 을 GitHub Secrets 의 YT_REFRESH_TOKEN_<채널> 에 넣는다.
   (토큰은 비밀번호와 같다. 채팅·저장소·메모 앱에 붙여넣지 말 것)
클라이언트는 Google Cloud 콘솔에서 'OAuth 클라이언트 ID → 데스크톱 앱'으로 만든다.
"""
from __future__ import annotations

import http.server
import json
import os
import sys
import urllib.parse
import urllib.request
import webbrowser

SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def main() -> int:
    cid, secret = os.environ.get("YT_CLIENT_ID"), os.environ.get("YT_CLIENT_SECRET")
    if not cid or not secret:
        print("YT_CLIENT_ID, YT_CLIENT_SECRET 환경 변수를 먼저 설정하세요.")
        return 1
    got: dict = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("완료! 이 창은 닫아도 됩니다.".encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    redirect = f"http://127.0.0.1:{srv.server_address[1]}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": SCOPE,
        "access_type": "offline", "prompt": "consent"})
    print("브라우저에서 로그인하세요:\n" + url)
    webbrowser.open(url)
    srv.handle_request()
    if "code" not in got:
        print("인증 코드를 받지 못했습니다:", got.get("error"))
        return 1
    data = urllib.parse.urlencode({"code": got["code"][0], "client_id": cid, "client_secret": secret,
                                   "redirect_uri": redirect, "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", data) as r:
        tok = json.loads(r.read())
    print("\nrefresh token (GitHub Secrets 에만 넣으세요):\n" + tok.get("refresh_token", "(없음 — prompt=consent 로 다시 시도)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
