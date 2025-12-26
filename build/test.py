import time
from nlp_query_engine import IntelligentNLPEngine

def run_test(query, description):
    print(f"\n📝 {description}")
    print(f"Query: '{query}'")
    engine = IntelligentNLPEngine()
    success, result = engine.execute(query)
    
    if success:
        print("✅ SUCCESS")
        print(f"Result preview: {str(result)[:100]}...")
    else:
        print(f"❌ FAILED: {result}")
    
    time.sleep(0.5)  # Rate limiting

# Test suite
tests = [
    ("show tables", "List all tables"),
    ("schema for employees", "Get schema"),
    ("show all employees", "Select all"),
    ("find employees where salary > 70000", "Numeric WHERE"),
    ("search employees where name contains Smith", "Text search"),
    ("join employees and departments", "JOIN tables"),
    ("stats for employees", "Get statistics"),
    ("show emplyees", "Typo handling"),
    ("staff earning more than 80k", "Synonym handling"),
    ("REFRESH", "Schema refresh")
]

print("🚀 Running NLP Test Suite...")
for query, desc in tests:
    run_test(query, desc)

print("\n✅ All tests completed!")