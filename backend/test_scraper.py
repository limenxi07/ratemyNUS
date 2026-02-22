from app.scraper import scrape_module_reviews

# Test with a known module
print("Testing CS1010...")
comments, error = scrape_module_reviews("CS1010")

if error:
    print(f"Error: {error}")
else:
    print(f"Success! Found {len(comments)} comments")
    if comments:
        print("\nFirst comment:")
        print(comments[0])

# Test with invalid module
print("\n\nTesting INVALID999...")
comments, error = scrape_module_reviews("INVALID999")
print(f"Error: {error}")

# Test with module that might have no reviews
print("\n\nTesting obscure module...")
comments, error = scrape_module_reviews("GEX1000")  # replace with actual obscure module
if error == "no_reviews":
    print("Correctly detected no reviews")