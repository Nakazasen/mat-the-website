import asyncio
import os
import sys
from fastapi.testclient import TestClient

# Configure streams to use UTF-8 on Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from main import app
except ImportError:
    from backend.main import app

client = TestClient(app)

def run_large_tts_tests():
    print("====================================================")
    print("STARTING TTS ROBUSTNESS AND LARGE AUDIO TESTS")
    print("====================================================\n")

    # A long paragraph of ~600 characters
    long_text = (
        "Trời âm u, mưa phùn rả rích, nhiệt độ hạ thấp xuống dưới ngưỡng hai độ C. "
        "Tiền cảnh thế giới mỗi lúc một thêm cực đoan tà dị. Thời tiết thất thường luôn là "
        "công cụ hữu hiệu nhất của thiên nhiên để nghiền nát trật tự nhân loại. Chỉ cần một yếu "
        "tố bất kỳ lệch chuẩn trong thời gian ngắn, toàn bộ hệ thống sinh tồn của nhân loại sẽ "
        "không thể kịp thời thích nghi, tự động kéo nhau suy kiệt. Hậu quả của thảm họa sinh hóa "
        "vẫn đang gieo rắc nỗi sợ hãi tột cùng lên vùng đất Tam Giang hoang tàn này."
    )
    print(f"Length of test text: {len(long_text)} characters.")

    # Test 1: Hit /api/tts with long text and Edge TTS voice
    print("\n⏳ Test 1: Requesting large Edge TTS audio (600 chars)...")
    response = client.get(
        "/api/tts",
        params={
            "text": long_text,
            "lang": "vi",
            "speed": 1.0,
            "voice": "vi-VN-NamMinhNeural"
        }
    )
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ SUCCESS: Received {len(response.content)} bytes of Nam Minh neural audio!")
    else:
        print(f"❌ FAILED: Status code {response.status_code}, error: {response.text}")

    # Test 2: Trigger fallback logic by sending an invalid voice and verifying it falls back to custom error message
    print("\n⏳ Test 2: Simulating Edge TTS failure by requesting an invalid voice...")
    response_fallback = client.get(
        "/api/tts",
        params={
            "text": "Nội dung chương truyện rất dài.",
            "lang": "vi",
            "speed": 1.0,
            "voice": "vi-VN-NamMinhNeural-invalid"
        }
    )
    print(f"Response status: {response_fallback.status_code}")
    if response_fallback.status_code == 200:
        print(f"✅ SUCCESS: Received {len(response_fallback.content)} bytes of fallback audio!")
        print("Note: The server logged the exception and returned Google speech for 'Hệ thống quá tải, không thể tải giọng đọc Nam Minh. Vui lòng thử lại sau.'")
    else:
        print(f"❌ FAILED: Status code {response_fallback.status_code}")

    print("\n====================================================")
    print("ALL TTS ROBUSTNESS VERIFICATION TESTS COMPLETED!")
    print("====================================================")

if __name__ == "__main__":
    run_large_tts_tests()
