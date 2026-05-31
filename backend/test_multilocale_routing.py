import asyncio
import os
import sys
from dotenv import load_dotenv

# Configure streams to use UTF-8 on Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    import main
except ImportError:
    from backend import main

async def test_chapter_translation():
    load_dotenv(override=True)
    
    print("========== REAL CHAPTER 828 TRANSLATION DIAGNOSIS ==========")
    
    # 1. Fetch chapter 828
    print("⏳ Fetching Chapter 828 metadata...")
    chapter_resp = (
        main.supabase.table("chapters")
        .select("*")
        .eq("chapter_number", 828)
        .single()
        .execute()
    )
    if not chapter_resp.data:
        print("❌ Error: Chapter 828 not found in database!")
        return
        
    chapter_row = chapter_resp.data
    print(f"Chapter Title: {chapter_row.get('title')}")
    
    # 2. Fetch content from R2
    print("⏳ Fetching Chapter 828 content from R2...")
    content_text = main.fetch_r2_content(chapter_row["content_url"])
    print(f"Content Length: {len(content_text)} characters")
    
    # Take a small snippet to avoid wasting massive tokens during test
    test_snippet = content_text[:1200]
    print(f"Test Snippet Length: {len(test_snippet)} characters")
    
    # 3. Rebuild router
    main.build_provider_router_from_config(force_rebuild=True)
    
    # 4. Attempt translation
    print("\n⏳ Running translate_chapter_payloads_with_ai with the snippet...")
    try:
        result = await main.translate_chapter_payloads_with_ai(
            title=chapter_row["title"],
            content=test_snippet,
            source_locale=main.DEFAULT_LOCALE,
            target_locales=["en", "zh-CN", "ja"],
            context_label="test-chapter-828",
            translation_mode="bulk"
        )
        print("✅ SUCCESS! Translation result locales:", list(result.keys()))
    except Exception as e:
        print("❌ FAILED with exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chapter_translation())
