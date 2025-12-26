# nlp_query_engine.py
import spacy
import numpy as np
import re
from fuzzywuzzy import fuzz
from typing import Dict, List, Any, Tuple
from api_client import DatabaseAPI

class IntelligentNLPEngine:
    def __init__(self, base_url: str = "http://localhost:8080"):
        print("Loading spaCy model... (en_core_web_md ~40MB)")
        try:
            self.nlp = spacy.load("en_core_web_md")
        except:
            import subprocess
            print("Downloading spaCy model...")
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_md"])
            self.nlp = spacy.load("en_core_web_md")
        
        self.db = DatabaseAPI(base_url)
        self.schema = self._load_schema()
        
        print(f"✅ Engine ready with schema: {list(self.schema.keys())}")
        
        self.operator_embeddings = self._build_operator_embeddings()
        self._enrich_vocab()
    
    def _load_schema(self) -> Dict[str, List[str]]:
        """Dynamically load schema from server"""
        try:
            tables = self.db.get_tables()
            schema = {}
            for table in tables:
                schema_data = self.db.get_schema(table)
                if "columns" in schema_data:
                    schema[table] = schema_data["columns"]
            return schema
        except:
            # Fallback
            return {
                "employees": ["empID", "name", "deptID", "salary", "position"],
                "departments": ["deptID", "deptName", "location"]
            }
    
    def _enrich_vocab(self):
        """Add table/column names to vocabulary"""
        for table, columns in self.schema.items():
            self.nlp.vocab[table].is_stop = False
            for col in columns:
                self.nlp.vocab[str(col)].is_stop = False
    
    def _build_operator_embeddings(self) -> Dict[str, np.ndarray]:
        operators = {
            ">": ["greater", "more", "higher", "above", "over", "exceeds", "more than"],
            "<": ["less", "lower", "below", "under", "fewer", "less than"],
            ">=": ["at least", "minimum", "no less than"],
            "<=": ["at most", "maximum", "no more than", "up to"],
            "=": ["equals", "is", "equal to", "exactly"],
            "!=": ["not", "not equal", "is not"],
            "like": ["contains", "search", "find", "like", "has", "with"]
        }
        
        op_vectors = {}
        for op, keywords in operators.items():
            vectors = [self.nlp(k).vector for k in keywords if self.nlp(k).has_vector]
            if vectors:
                op_vectors[op] = np.mean(vectors, axis=0)
        
        return op_vectors
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        doc1 = self.nlp(text1.lower())
        doc2 = self.nlp(text2.lower())
        return doc1.similarity(doc2)
    
    def extract_table(self, doc) -> str:
        candidates = set()
        candidates.update([token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]])
        candidates.update([chunk.text for chunk in doc.noun_chunks])
        candidates.update([ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "GPE"]])
        
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            for table_name in self.schema.keys():
                fuzzy_score = fuzz.ratio(candidate.lower(), table_name.lower())
                sem_score = self.nlp(candidate).similarity(self.nlp(table_name))
                combined = max(fuzzy_score / 100, sem_score)
                
                if combined > best_score and combined > 0.75:
                    best_match = table_name
                    best_score = combined
        
        return best_match
    
    def extract_column(self, doc, table: str) -> str:
        if table not in self.schema:
            return None
        
        columns = self.schema[table]
        candidates = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]]
        candidates += [chunk.text for chunk in doc.noun_chunks]
        
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            for col in columns:
                fuzzy_score = fuzz.ratio(candidate.lower(), str(col).lower())
                sem_score = self.nlp(candidate).similarity(self.nlp(str(col)))
                combined = max(fuzzy_score / 100, sem_score)
                
                if combined > best_score and combined > 0.7:
                    best_match = str(col)
                    best_score = combined
        
        return best_match
    
    def extract_operator(self, doc) -> str:
        doc_vector = np.mean([token.vector for token in doc if token.has_vector], axis=0)
        
        if np.linalg.norm(doc_vector) == 0:
            return "="
        
        best_op = "="
        best_sim = 0
        
        for op, op_vector in self.operator_embeddings.items():
            if np.linalg.norm(op_vector) == 0:
                continue
            sim = np.dot(doc_vector, op_vector) / (np.linalg.norm(doc_vector) * np.linalg.norm(op_vector))
            if sim > best_sim and sim > 0.6:
                best_op = op
                best_sim = sim
        
        return best_op
    
    def extract_value(self, doc, column: str = None) -> str:
        # Numbers
        for token in doc:
            if token.like_num or token.pos_ == "NUM":
                return token.text
        
        # Quoted strings
        quotes = re.findall(r"['\"]([^'\"]+)['\"]", doc.text)
        if quotes:
            return quotes[0]
        
        # Proper nouns
        proper_nouns = [token.text for token in doc if token.pos_ == "PROPN"]
        if proper_nouns:
            return " ".join(proper_nouns)
        
        # Last noun chunk
        noun_chunks = list(doc.noun_chunks)
        if noun_chunks:
            for chunk in reversed(noun_chunks):
                if chunk.text not in self.schema and chunk.text not in str(self.schema.values()):
                    return chunk.text
        
        return None
    
    def _classify_intent(self, doc) -> str:
        test_phrases = {
            "health": "health status check",
            "tables": "show tables list tables",
            "schema": "show schema structure columns",
            "stats": "statistics count rows stats",
            "join": "join combine merge tables",
            "search": "search find contains like",
            "select_where": "where filter condition",
            "select_all": "show all list get display"
        }
        
        similarities = {intent: self.semantic_similarity(doc.text, phrase) 
                       for intent, phrase in test_phrases.items()}
        
        best_intent = max(similarities, key=similarities.get)
        
        # Keyword boost
        if "join" in doc.text.lower():
            return "join"
        if "search" in doc.text.lower() or "contains" in doc.text.lower():
            return "search"
        if "schema" in doc.text.lower():
            return "schema"
        if "stats" in doc.text.lower():
            return "stats"
        
        return best_intent
    
    def extract_join_tables(self, doc) -> List[str]:
        candidates = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]]
        candidates += [chunk.text for chunk in doc.noun_chunks]
        
        found_tables = []
        for candidate in candidates:
            for table_name in self.schema.keys():
                if candidate.lower() == table_name.lower() and table_name not in found_tables:
                    found_tables.append(table_name)
        
        return found_tables[:2]
    
    def execute(self, query: str) -> Tuple[bool, Any]:
        """Direct execution (NO _execute_with_dynamic_schema call)"""
        doc = self.nlp(query.lower())
        
        # Auto-refresh schema
        if not hasattr(self, '_schema_loaded') or self._schema_loaded is False:
            self.schema = self._load_schema()
            self._schema_loaded = True
        
        intent = self._classify_intent(doc)
        
        # Handle intents directly
        if intent == "health":
            return True, self.db.health_check()
        
        elif intent == "tables":
            return True, self.db.get_tables()
        
        elif intent == "schema":
            table = self.extract_table(doc)
            if not table:
                return False, f"Which table? Available: {list(self.schema.keys())}"
            return True, self.db.get_schema(table)
        
        elif intent == "stats":
            table = self.extract_table(doc)
            if not table:
                return False, f"Which table? Available: {list(self.schema.keys())}"
            return True, self.db.get_stats(table)
        
        elif intent == "join":
            tables = self.extract_join_tables(doc)
            if len(tables) < 2:
                return False, f"Need 2 tables. Found: {tables}"
            return True, self.db.join(tables[0], tables[1])
        
        elif intent == "search":
            table = self.extract_table(doc)
            if not table:
                return False, f"Which table? Available: {list(self.schema.keys())}"
            column = self.extract_column(doc, table)
            keyword = self.extract_value(doc)
            if not all([table, column, keyword]):
                return False, f"Missing: table={table}, column={column}, keyword={keyword}"
            return True, self.db.search(table, column, keyword)
        
        elif intent == "select_where":
            table = self.extract_table(doc)
            if not table:
                return False, f"Which table? Available: {list(self.schema.keys())}"
            column = self.extract_column(doc, table)
            operator = self.extract_operator(doc)
            value = self.extract_value(doc)
            if not all([table, column, value]):
                return False, f"Missing: table={table}, column={column}, value={value}"
            return True, self.db.query(table, column, operator, value)
        
        elif intent == "select_all":
            table = self.extract_table(doc)
            if not table:
                return False, f"Which table? Available: {list(self.schema.keys())}"
            return True, self.db.get_table(table)
        
        return False, f"Unknown intent: {intent}"
    
    def refresh_schema(self):
        self.schema = self._load_schema()
        self._enrich_vocab()