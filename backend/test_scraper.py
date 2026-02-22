from app.scraper import scrape_module_reviews

# Test with a known module
print("Testing CS1101S...")
comments, error = scrape_module_reviews("CS1101S")

if error:
    print(f"Error: {error}")
else:
    print(f"Success! Found {len(comments)} comments")
    if comments:
        print(f"\nFirst comment: {comments[0]}")
        print(f"\nLast comment: {comments[-1]}")