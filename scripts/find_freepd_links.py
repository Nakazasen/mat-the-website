import urllib.request

urls = {
    "Deep Noise": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Deep%20Noise.mp3",
    "The Descent": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20Descent.mp3",
    "Cryptic Sorrow": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cryptic%20Sorrow.mp3"
}

for name, url in urls.items():
    print(f"Testing {name}: {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            info = response.info()
            print(f" -> Success! {info.get('Content-Length')} bytes")
    except Exception as e:
        print(f" -> Failed: {e}")
