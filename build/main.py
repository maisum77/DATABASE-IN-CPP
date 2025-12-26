# main.py
from nlp_query_engine import IntelligentNLPEngine
import json

def main():
    engine = IntelligentNLPEngine()
    
    print("🧠 AI Query Engine (Dynamic Schema)")
    print("Commands: REFRESH, quit")
    print("Examples:")
    print("  'Show employees earning more than 70000'")
    print("  'Find people named Smith'")
    print("  'Join employees with departments'")
    print("-" * 60)
    
    while True:
        try:
            query = input("\n>>> ").strip()
            
            if query.upper() == "REFRESH":
                engine.refresh_schema()
                continue
            
            if query.lower() in ["quit", "exit", "q"]:
                break
            
            if not query:
                continue
            
            print(f"\n🔍 Processing: '{query}'\n")
            success, result = engine.execute(query)
            
            if success:
                print("✅ Result:")
                if isinstance(result, list) and result and isinstance(result[0], list):
                    from tabulate import tabulate
                    print(tabulate(result, headers="firstrow", tablefmt="grid"))
                else:
                    print(json.dumps(result, indent=2))
            else:
                print(f"❌ {result}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()