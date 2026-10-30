import os
import time
import requests

BASE = "https://api.heygen.com"


class HeyGenError(RuntimeError):
    pass


class HeyGenClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("HEYGEN_API_KEY")
        if not self.api_key:
            raise HeyGenError("HEYGEN_API_KEY is not set (see .env.example)")
        self.s = requests.Session()
        self.s.headers.update({"X-Api-Key": self.api_key, "Accept": "application/json"})

    def _req(self, method, path, **kw):
        r = self.s.request(method, BASE + path, timeout=60, **kw)
        if r.status_code >= 400:
            raise HeyGenError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        body = r.json()
        if body.get("error"):
            raise HeyGenError(f"{path}: {body['error']}")
        return body.get("data", body)

    def list_avatars(self):
        return self._req("GET", "/v2/avatars").get("avatars", [])

    def list_voices(self):
        return self._req("GET", "/v2/voices").get("voices", [])

    @staticmethod
    def build_payload(title, scenes, p):
        bg = (
            {"type": "image", "url": p.background}
            if p.background.startswith("http")
            else {"type": "color", "value": p.background}
        )
        return {
            "title": title,
            "dimension": {"width": p.width, "height": p.height},
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": p.avatar_id,
                        "avatar_style": p.avatar_style,
                    },
                    "voice": {"type": "text", "input_text": t, "voice_id": p.voice_id},
                    "background": bg,
                }
                for t in scenes
            ],
        }

    def create_video(self, payload) -> str:
        return self._req("POST", "/v2/video/generate", json=payload)["video_id"]

    def status(self, video_id):
        return self._req("GET", "/v1/video_status.get", params={"video_id": video_id})

    def wait(self, video_id, poll=15, timeout_min=30, on_tick=None):
        deadline = time.time() + timeout_min * 60
        while time.time() < deadline:
            d = self.status(video_id)
            st = d.get("status")
            if on_tick:
                on_tick(st)
            if st == "completed":
                return d
            if st == "failed":
                raise HeyGenError(f"Video {video_id} failed: {d.get('error')}")
            time.sleep(poll)
        raise HeyGenError(f"Timed out waiting for {video_id}")

    def download(self, url, dest):
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
