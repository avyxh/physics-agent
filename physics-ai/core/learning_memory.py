# core/learning_memory.py
import json
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from utils.data_models import PhysicsProblem, Solution, VerificationResult

class LearningMemory:
    def __init__(self, db_path: str = "data/physics_memory.db"):
        self.db_path = db_path
        self._ensure_db_exists()
        self.success_patterns = {}
        self.error_patterns = {}
        self.user_preferences = {}
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problem_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_hash TEXT UNIQUE,
                problem_text TEXT,
                problem_type TEXT,
                solution_method TEXT,
                analytical_result TEXT,
                simulation_result TEXT,
                agreement_score REAL,
                confidence REAL,
                timestamp TEXT,
                was_correct BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT,
                problem_type TEXT,
                description TEXT,
                frequency INTEGER DEFAULT 1,
                last_seen TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS success_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method_name TEXT,
                problem_type TEXT,
                success_rate REAL,
                avg_confidence REAL,
                usage_count INTEGER DEFAULT 1,
                last_used TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_problem_solution(self, problem: PhysicsProblem, solution: Solution, 
                             verification: VerificationResult, was_correct: bool = True):
        """Store a solved problem and its results for learning"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create unique hash for problem
        problem_hash = self._hash_problem(problem.problem_text)
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO problem_history 
                (problem_hash, problem_text, problem_type, solution_method,
                 analytical_result, simulation_result, agreement_score, 
                 confidence, timestamp, was_correct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                problem_hash,
                problem.problem_text,
                problem.problem_type.value,
                solution.method,
                str(solution.answer),
                str(verification.simulation_result),
                verification.agreement_score,
                verification.confidence,
                datetime.now().isoformat(),
                was_correct
            ))
            
            # Update success patterns
            self._update_success_pattern(solution.method, problem.problem_type.value, 
                                       verification.confidence, was_correct)
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    
    def store_error_pattern(self, error_type: str, problem_type: str, description: str):
        """Store information about errors for learning"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if this error pattern already exists
            cursor.execute('''
                SELECT id, frequency FROM error_patterns 
                WHERE error_type = ? AND problem_type = ?
            ''', (error_type, problem_type))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing pattern
                cursor.execute('''
                    UPDATE error_patterns 
                    SET frequency = frequency + 1, last_seen = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), result[0]))
            else:
                # Insert new pattern
                cursor.execute('''
                    INSERT INTO error_patterns 
                    (error_type, problem_type, description, last_seen)
                    VALUES (?, ?, ?, ?)
                ''', (error_type, problem_type, description, datetime.now().isoformat()))
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error storing error pattern: {e}")
        finally:
            conn.close()
    
    def get_best_method_for_problem(self, problem_type: str) -> Optional[str]:
        """Get the most successful method for a given problem type"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT method_name, success_rate, avg_confidence
                FROM success_patterns 
                WHERE problem_type = ?
                ORDER BY success_rate DESC, avg_confidence DESC
                LIMIT 1
            ''', (problem_type,))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except sqlite3.Error as e:
            print(f"Error retrieving best method: {e}")
            return None
        finally:
            conn.close()
    
    def get_similar_problems(self, problem_text: str, limit: int = 5) -> List[Dict]:
        """Find similar problems solved before"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Simple similarity based on common words
            # In a real system, you'd use more sophisticated NLP
            keywords = set(problem_text.lower().split())
            
            cursor.execute('''
                SELECT problem_text, solution_method, analytical_result, 
                       confidence, timestamp
                FROM problem_history 
                WHERE was_correct = 1
                ORDER BY confidence DESC
                LIMIT ?
            ''', (limit * 3,))  # Get more to filter
            
            results = cursor.fetchall()
            similar_problems = []
            
            for result in results:
                stored_problem = result[0]
                stored_keywords = set(stored_problem.lower().split())
                
                # Calculate simple similarity score
                common_words = keywords.intersection(stored_keywords)
                similarity = len(common_words) / max(len(keywords), len(stored_keywords))
                
                if similarity > 0.3:  # Threshold for similarity
                    similar_problems.append({
                        'problem_text': stored_problem,
                        'method': result[1],
                        'result': result[2],
                        'confidence': result[3],
                        'similarity': similarity,
                        'timestamp': result[4]
                    })
            
            # Sort by similarity and return top results
            similar_problems.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_problems[:limit]
            
        except sqlite3.Error as e:
            print(f"Error finding similar problems: {e}")
            return []
        finally:
            conn.close()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about system performance and learning"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        insights = {}
        
        try:
            # Overall statistics
            cursor.execute('SELECT COUNT(*) FROM problem_history')
            insights['total_problems_solved'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(confidence) FROM problem_history WHERE was_correct = 1')
            result = cursor.fetchone()
            insights['average_confidence'] = result[0] if result[0] else 0
            
            cursor.execute('SELECT AVG(agreement_score) FROM problem_history')
            result = cursor.fetchone()
            insights['average_agreement'] = result[0] if result[0] else 0
            
            # Most successful methods
            cursor.execute('''
                SELECT method_name, success_rate, usage_count
                FROM success_patterns 
                ORDER BY success_rate DESC, usage_count DESC
                LIMIT 5
            ''')
            insights['top_methods'] = cursor.fetchall()
            
            # Common error patterns
            cursor.execute('''
                SELECT error_type, problem_type, frequency
                FROM error_patterns 
                ORDER BY frequency DESC
                LIMIT 5
            ''')
            insights['common_errors'] = cursor.fetchall()
            
            # Problem type distribution
            cursor.execute('''
                SELECT problem_type, COUNT(*) 
                FROM problem_history 
                GROUP BY problem_type
                ORDER BY COUNT(*) DESC
            ''')
            insights['problem_type_distribution'] = cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Error generating insights: {e}")
        finally:
            conn.close()
        
        return insights
    
    def _hash_problem(self, problem_text: str) -> str:
        """Create a unique hash for a problem"""
        return hashlib.md5(problem_text.encode()).hexdigest()
    
    def _update_success_pattern(self, method: str, problem_type: str, 
                              confidence: float, was_correct: bool):
        """Update success patterns for a method"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get existing pattern
            cursor.execute('''
                SELECT id, success_rate, avg_confidence, usage_count
                FROM success_patterns 
                WHERE method_name = ? AND problem_type = ?
            ''', (method, problem_type))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing pattern
                pattern_id, old_success_rate, old_avg_confidence, usage_count = result
                
                new_usage_count = usage_count + 1
                new_success_rate = (old_success_rate * usage_count + (1 if was_correct else 0)) / new_usage_count
                new_avg_confidence = (old_avg_confidence * usage_count + confidence) / new_usage_count
                
                cursor.execute('''
                    UPDATE success_patterns 
                    SET success_rate = ?, avg_confidence = ?, usage_count = ?, last_used = ?
                    WHERE id = ?
                ''', (new_success_rate, new_avg_confidence, new_usage_count, 
                      datetime.now().isoformat(), pattern_id))
            else:
                # Create new pattern
                cursor.execute('''
                    INSERT INTO success_patterns 
                    (method_name, problem_type, success_rate, avg_confidence, last_used)
                    VALUES (?, ?, ?, ?, ?)
                ''', (method, problem_type, 1 if was_correct else 0, confidence, 
                      datetime.now().isoformat()))
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error updating success pattern: {e}")
        finally:
            conn.close()