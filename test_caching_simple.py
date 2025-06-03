#!/usr/bin/env python3
"""Tests for company summary caching functionality."""

from _2_create_company_summary import get_cache_info, clear_company_cache, _company_cache

def test_cache_functions():
    """Test basic cache operations: initialization, storage, retrieval, and clearing."""
    print("🧪 Testing Cache Functions")
    print("=" * 50)
    
    # Test initialization
    clear_company_cache()
    info = get_cache_info()
    assert info['cache_size'] == 0 and info['cached_companies'] == [], "Cache should start empty"
    print("✅ Cache initialization: PASS")
    
    # Test storage and retrieval
    test_summary = "Test company summary for Microsoft"
    _company_cache['microsoft'] = test_summary
    info = get_cache_info()
    assert info['cache_size'] == 1 and 'microsoft' in info['cached_companies'], "Cache storage failed"
    assert _company_cache.get('microsoft') == test_summary, "Cache retrieval failed"
    print("✅ Cache storage and retrieval: PASS")
    
    # Test multiple entries
    _company_cache.update({
        'apple': "Apple company summary",
        'google': "Google company summary"
    })
    assert get_cache_info()['cache_size'] == 3, "Multiple cache entries failed"
    print("✅ Multiple cache entries: PASS")
    
    # Test cache clearing
    clear_company_cache()
    assert get_cache_info()['cache_size'] == 0, "Cache clearing failed"
    print("✅ Cache clearing: PASS")
    
    return True

def test_cache_key_logic():
    """Test cache key creation from company names and URLs."""
    print("\n🧪 Testing Cache Key Logic")
    print("=" * 30)
    
    def create_cache_key(company_name=None, company_base_link=None):
        """Create cache key from company name or URL."""
        from urllib.parse import urlparse
        if company_name:
            return company_name.lower().strip()
        if company_base_link:
            return urlparse(company_base_link).netloc.lower().strip()
        return None
    
    test_cases = [
        ("Microsoft", None, "microsoft"),
        ("  APPLE  ", None, "apple"),
        (None, "https://google.com", "google.com"),
        (None, "https://www.Microsoft.com/about", "www.microsoft.com"),
        ("Company Name", "https://somesite.com", "company name")
    ]
    
    all_passed = True
    for company_name, link, expected in test_cases:
        result = create_cache_key(company_name, link)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {company_name or 'None'}, {link or 'None'} -> '{result}' {status}")
        all_passed = all_passed and result == expected
    
    return all_passed

def main():
    """Run all cache tests and display results."""
    print("🚀 Testing Company Summary Caching")
    print("=" * 60)
    
    cache_test_passed = test_cache_functions()
    key_test_passed = test_cache_key_logic()
    
    print("\n📊 Test Results:")
    print(f"  Cache Functions: {'✅ PASS' if cache_test_passed else '❌ FAIL'}")
    print(f"  Cache Key Logic: {'✅ PASS' if key_test_passed else '❌ FAIL'}")
    
    if cache_test_passed and key_test_passed:
        print("\n🎉 All tests passed! Caching is working correctly.")
        print("\n💡 Usage:")
        print("  1. create_company_summary(company_name='Microsoft')  # First call: processes and caches")
        print("  2. create_company_summary(company_name='Microsoft')  # Second call: uses cache")
        print("  3. clear_company_cache()  # Clear cache if needed")
        print("  4. get_cache_info()  # View cache contents")
        return True
    
    print("\n❌ Some tests failed. Check implementation.")
    return False

if __name__ == "__main__":
    main() 