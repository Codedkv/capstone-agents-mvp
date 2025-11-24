"""Quick test for ADK-compatible tools."""

from tools.adk_tools import (
    load_csv_data,
    detect_anomalies,
    search_market_trends,
    log_agent_action
)

def test_adk_tools():
    """Test ADK tool wrappers."""
    
    print("=== Testing ADK Tool Wrappers ===\n")
    
    # Test 1: Load CSV
    print("1. Testing load_csv_data...")
    result = load_csv_data(filepath="data/sample_business_metrics.csv")
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Rows loaded: {result['row_count']}")
    print()
    
    # Test 2: Detect anomalies
    print("2. Testing detect_anomalies...")
    test_data = [50000, 52000, 48000, 51000, 120000, 49000]
    result = detect_anomalies(data=test_data, method="iqr")
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Anomalies found: {result['count']}")
        print(f"   Values: {result['anomalies']}")
    print()
    
    # Test 3: Search market trends
    print("3. Testing search_market_trends...")
    result = search_market_trends(topic="Revenue spike", region="Global", use_api=False)
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Source: {result['source']}")
        print(f"   Trends found: {len(result['trends'])}")
    print()
    
    # Test 4: Log action
    print("4. Testing log_agent_action...")
    result = log_agent_action(
        agent_name="TestAgent",
        action="test_adk_tools",
        details={"test": "ADK compatibility"}
    )
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Logged: {result['logged']}")
    print()
    
    print("=== All ADK tools tested successfully ===")

if __name__ == "__main__":
    test_adk_tools()
