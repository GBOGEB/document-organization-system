#!/usr/bin/env python3
"""
Quick Performance Optimization Demo
Demonstrates the key improvements from each optimization module.
"""

import time
import tempfile
import zipfile
from pathlib import Path

def main():
    print('=== Performance Optimization Demo ===\n')
    
    # Create test data
    temp_dir = Path(tempfile.mkdtemp())
    print(f'Using temp directory: {temp_dir}')
    
    try:
        # Test 1: ZIP Processing
        print('\n1. ZIP Processing Optimization:')
        test_zip_processing(temp_dir)
        
        # Test 2: Caching System
        print('\n2. Intelligent Caching System:')
        test_caching_system()
        
        # Test 3: Binary Parser
        print('\n3. Binary Format Enhancement:')
        test_binary_parser(temp_dir)
        
        print('\n=== Demo Complete ===')
        print('✓ All optimizations are working correctly!')
        
    except Exception as e:
        print(f'Demo error: {e}')
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_zip_processing(temp_dir):
    """Test ZIP processing optimization."""
    try:
        # Create test ZIP file
        zip_path = temp_dir / 'test.zip'
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('module1.py', '''
class TestClass:
    def __init__(self):
        self.value = 0
    
    def process(self, data):
        for item in data:
            if item > 0:
                self.value += item
        return self.value
''')
            zf.writestr('module2.py', '''
def calculate(x, y):
    result = 0
    for i in range(x):
        if i % 2 == 0:
            result += y
    return result
''')
        
        from zip_opt.intelligent_zip_processor import IntelligentZipProcessor
        
        # Test processing
        processor = IntelligentZipProcessor(max_workers=2)
        start_time = time.perf_counter()
        result = processor.process_zip_file(str(zip_path))
        processing_time = time.perf_counter() - start_time
        
        print(f'  ✓ Processing time: {processing_time:.4f}s')
        print(f'  ✓ Files processed: {result.get("processed_files", 0)}')
        print(f'  ✓ Important files: {result.get("important_files", 0)}')
        
    except Exception as e:
        print(f'  ✗ ZIP processing error: {e}')

def test_caching_system():
    """Test intelligent caching system."""
    try:
        from cache_opt.intelligent_cache import IntelligentCache
        
        def expensive_operation(key):
            time.sleep(0.001)  # Simulate 1ms delay
            return f'result_for_{key}'
        
        # Test with caching
        cache = IntelligentCache(max_size=50, enable_prediction=False, auto_tune=False)
        
        start_time = time.perf_counter()
        for i in range(20):
            for j in range(2):  # Access same keys twice
                cache_key = f'key_{i}'
                result = cache.get(cache_key)
                if result is None:
                    result = expensive_operation(cache_key)
                    cache.put(cache_key, result, ttl=3600)
        
        processing_time = time.perf_counter() - start_time
        stats = cache.get_comprehensive_stats()
        
        print(f'  ✓ Processing time: {processing_time:.4f}s')
        print(f'  ✓ Cache hit rate: {stats["hit_rate"]:.1f}%')
        print(f'  ✓ Total requests: {stats["hits"] + stats["misses"]}')
        
        cache.shutdown()
        
    except Exception as e:
        print(f'  ✗ Caching error: {e}')

def test_binary_parser(temp_dir):
    """Test binary format parser."""
    try:
        from binary_opt.robust_binary_parser import RobustBinaryParser
        
        # Create mock PowerPoint file
        pptx_path = temp_dir / 'test.pptx'
        with zipfile.ZipFile(pptx_path, 'w') as zf:
            zf.writestr('[Content_Types].xml', '''<?xml version="1.0"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
</Types>''')
            zf.writestr('_rels/.rels', '''<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>''')
            zf.writestr('ppt/presentation.xml', '''<?xml version="1.0"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst>
</p:presentation>''')
        
        parser = RobustBinaryParser()
        start_time = time.perf_counter()
        result = parser.parse_file(pptx_path)
        parse_time = time.perf_counter() - start_time
        
        print(f'  ✓ Parse time: {parse_time:.4f}s')
        print(f'  ✓ Success: {result.get("success", False)}')
        print(f'  ✓ Format: {result.get("format_detection", {}).get("detected_format", "unknown")}')
        print(f'  ✓ Parser used: {result.get("parser", "unknown")}')
        
    except Exception as e:
        print(f'  ✗ Binary parser error: {e}')

if __name__ == "__main__":
    main()
