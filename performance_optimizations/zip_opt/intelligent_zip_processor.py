"""
Intelligent ZIP Processing Optimization
Implements AST-based Python code analysis with parallel processing and smart caching.
"""

import ast
import asyncio
import concurrent.futures
import hashlib
import json
import logging
import multiprocessing as mp
import os
import time
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import diskcache as dc


class PythonCodeAnalyzer:
    """AST-based Python code analyzer for intelligent processing."""
    
    def __init__(self):
        self.importance_weights = {
            'class_definitions': 10,
            'function_definitions': 8,
            'imports': 6,
            'decorators': 7,
            'docstrings': 5,
            'complexity_score': 1,
            'lines_of_code': 0.1
        }
    
    def analyze_code(self, code_content: str, filename: str) -> Dict[str, Any]:
        """Analyze Python code using AST parsing."""
        try:
            tree = ast.parse(code_content)
            analysis = {
                'filename': filename,
                'classes': [],
                'functions': [],
                'imports': [],
                'decorators': [],
                'docstrings': [],
                'complexity_score': 0,
                'lines_of_code': len(code_content.splitlines()),
                'importance_score': 0
            }
            
            analyzer = CodeVisitor()
            analyzer.visit(tree)
            
            analysis.update({
                'classes': analyzer.classes,
                'functions': analyzer.functions,
                'imports': analyzer.imports,
                'decorators': analyzer.decorators,
                'docstrings': analyzer.docstrings,
                'complexity_score': analyzer.complexity_score
            })
            
            # Calculate importance score
            analysis['importance_score'] = self._calculate_importance_score(analysis)
            
            return analysis
            
        except SyntaxError as e:
            logging.warning(f"Syntax error in {filename}: {e}")
            return self._create_fallback_analysis(filename, code_content)
        except Exception as e:
            logging.error(f"Error analyzing {filename}: {e}")
            return self._create_fallback_analysis(filename, code_content)
    
    def _calculate_importance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate file importance score based on various metrics."""
        score = 0
        score += len(analysis['classes']) * self.importance_weights['class_definitions']
        score += len(analysis['functions']) * self.importance_weights['function_definitions']
        score += len(analysis['imports']) * self.importance_weights['imports']
        score += len(analysis['decorators']) * self.importance_weights['decorators']
        score += len(analysis['docstrings']) * self.importance_weights['docstrings']
        score += analysis['complexity_score'] * self.importance_weights['complexity_score']
        score += analysis['lines_of_code'] * self.importance_weights['lines_of_code']
        
        return score
    
    def _create_fallback_analysis(self, filename: str, content: str) -> Dict[str, Any]:
        """Create fallback analysis for files that can't be parsed."""
        return {
            'filename': filename,
            'classes': [],
            'functions': [],
            'imports': [],
            'decorators': [],
            'docstrings': [],
            'complexity_score': 0,
            'lines_of_code': len(content.splitlines()),
            'importance_score': len(content.splitlines()) * 0.1,
            'parse_error': True
        }


class CodeVisitor(ast.NodeVisitor):
    """AST visitor for extracting code metrics."""
    
    def __init__(self):
        self.classes = []
        self.functions = []
        self.imports = []
        self.decorators = []
        self.docstrings = []
        self.complexity_score = 0
    
    def visit_ClassDef(self, node):
        self.classes.append({
            'name': node.name,
            'line': node.lineno,
            'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
            'decorators': len(node.decorator_list)
        })
        self.complexity_score += 2
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'args': len(node.args.args),
            'decorators': len(node.decorator_list)
        })
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({
                'name': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append({
                'module': node.module,
                'name': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
    
    def visit_If(self, node):
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity_score += 1
        self.generic_visit(node)
    
    def visit_Try(self, node):
        self.complexity_score += 1
        self.generic_visit(node)


class SmartZipCache:
    """Smart caching system for ZIP analysis results."""
    
    def __init__(self, cache_dir: str = "./zip_cache"):
        self.cache = dc.Cache(cache_dir)
        self.hit_count = 0
        self.miss_count = 0
    
    def get_cache_key(self, zip_path: str, file_path: str) -> str:
        """Generate cache key based on ZIP file and internal file."""
        zip_stat = os.stat(zip_path)
        key_data = f"{zip_path}:{file_path}:{zip_stat.st_mtime}:{zip_stat.st_size}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, zip_path: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        key = self.get_cache_key(zip_path, file_path)
        result = self.cache.get(key)
        if result:
            self.hit_count += 1
        else:
            self.miss_count += 1
        return result
    
    def set(self, zip_path: str, file_path: str, analysis: Dict[str, Any], expire: int = 3600):
        """Cache analysis result."""
        key = self.get_cache_key(zip_path, file_path)
        self.cache.set(key, analysis, expire=expire)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        return {
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache)
        }


class IntelligentZipProcessor:
    """Main ZIP processor with intelligent analysis and parallel processing."""
    
    def __init__(self, max_workers: Optional[int] = None, cache_dir: str = "./zip_cache"):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.analyzer = PythonCodeAnalyzer()
        self.cache = SmartZipCache(cache_dir)
        self.logger = logging.getLogger(__name__)
        
        # File type priorities for selective extraction
        self.file_priorities = {
            '.py': 10,
            '.pyx': 9,
            '.pyi': 8,
            '.ipynb': 7,
            '.md': 5,
            '.txt': 3,
            '.json': 4,
            '.yaml': 4,
            '.yml': 4,
            '.toml': 4,
            '.cfg': 3,
            '.ini': 3
        }
    
    def process_zip_file(self, zip_path: str, selective: bool = True, 
                        importance_threshold: float = 5.0) -> Dict[str, Any]:
        """Process ZIP file with intelligent analysis."""
        start_time = time.perf_counter()
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Filter files based on priorities if selective mode is enabled
                if selective:
                    file_list = self._filter_files_by_priority(file_list)
                
                # Process files in parallel
                results = self._process_files_parallel(zip_file, file_list, zip_path)
                
                # Filter by importance threshold
                important_files = [
                    result for result in results 
                    if result and result.get('importance_score', 0) >= importance_threshold
                ]
                
                processing_time = time.perf_counter() - start_time
                
                return {
                    'zip_path': zip_path,
                    'total_files': len(file_list),
                    'processed_files': len(results),
                    'important_files': len(important_files),
                    'processing_time': processing_time,
                    'cache_stats': self.cache.get_stats(),
                    'results': important_files,
                    'all_results': results
                }
                
        except Exception as e:
            self.logger.error(f"Error processing ZIP file {zip_path}: {e}")
            return {
                'zip_path': zip_path,
                'error': str(e),
                'processing_time': time.perf_counter() - start_time
            }
    
    def _filter_files_by_priority(self, file_list: List[str]) -> List[str]:
        """Filter files based on extension priorities."""
        prioritized_files = []
        
        for file_path in file_list:
            ext = Path(file_path).suffix.lower()
            if ext in self.file_priorities:
                prioritized_files.append((file_path, self.file_priorities[ext]))
        
        # Sort by priority (descending) and return file paths
        prioritized_files.sort(key=lambda x: x[1], reverse=True)
        return [file_path for file_path, _ in prioritized_files]
    
    def _process_files_parallel(self, zip_file: zipfile.ZipFile, 
                               file_list: List[str], zip_path: str) -> List[Dict[str, Any]]:
        """Process files in parallel using ThreadPoolExecutor."""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_single_file, zip_file, file_path, zip_path): file_path
                for file_path in file_list
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
        
        return results
    
    def _process_single_file(self, zip_file: zipfile.ZipFile, 
                           file_path: str, zip_path: str) -> Optional[Dict[str, Any]]:
        """Process a single file from the ZIP archive."""
        # Check cache first
        cached_result = self.cache.get(zip_path, file_path)
        if cached_result:
            return cached_result
        
        try:
            # Read file content
            with zip_file.open(file_path) as file:
                content = file.read()
            
            # Decode content
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = content.decode('latin-1')
                except UnicodeDecodeError:
                    self.logger.warning(f"Could not decode {file_path}")
                    return None
            
            # Analyze based on file type
            ext = Path(file_path).suffix.lower()
            if ext == '.py':
                analysis = self.analyzer.analyze_code(text_content, file_path)
            else:
                # Basic analysis for non-Python files
                analysis = {
                    'filename': file_path,
                    'file_type': ext,
                    'size': len(content),
                    'lines_of_code': len(text_content.splitlines()),
                    'importance_score': len(text_content.splitlines()) * 0.05
                }
            
            # Cache the result
            self.cache.set(zip_path, file_path, analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def batch_process_zips(self, zip_paths: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple ZIP files in parallel."""
        results = []
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_zip = {
                executor.submit(self._process_zip_worker, zip_path, kwargs): zip_path
                for zip_path in zip_paths
            }
            
            for future in concurrent.futures.as_completed(future_to_zip):
                zip_path = future_to_zip[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing ZIP {zip_path}: {e}")
                    results.append({
                        'zip_path': zip_path,
                        'error': str(e)
                    })
        
        return results
    
    @staticmethod
    def _process_zip_worker(zip_path: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Worker function for processing ZIP files in separate processes."""
        processor = IntelligentZipProcessor()
        return processor.process_zip_file(zip_path, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    processor = IntelligentZipProcessor()
    
    # Process a single ZIP file
    # result = processor.process_zip_file("example.zip")
    # print(json.dumps(result, indent=2))
    
    print("Intelligent ZIP Processor initialized successfully!")
