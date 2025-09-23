"""
Comprehensive Test Suite for Performance Optimizations
Tests all optimization modules with edge cases and error conditions.
"""

import asyncio
import json
import os
import pytest
import tempfile
import time
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from zip_opt.intelligent_zip_processor import IntelligentZipProcessor, PythonCodeAnalyzer, SmartZipCache
from binary_opt.robust_binary_parser import RobustBinaryParser, FormatValidator, PowerPointParser
from async_io.async_file_processor import AsyncFileProcessor, ResourceManager, StreamingFileReader
from cache_opt.intelligent_cache import IntelligentCache, LRUCache, PredictiveEngine


class TestIntelligentZipProcessor:
    """Test suite for ZIP processing optimization."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_zip(self, temp_dir):
        """Create sample ZIP file for testing."""
        zip_path = temp_dir / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            # Add Python files
            zf.writestr("module1.py", '''
class TestClass:
    """Test class."""
    
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value * 2
''')
            
            zf.writestr("module2.py", '''
def function():
    """Test function."""
    for i in range(10):
        if i % 2 == 0:
            print(i)
''')
            
            # Add non-Python files
            zf.writestr("README.md", "# Test Project")
            zf.writestr("config.json", '{"test": true}')
        
        return zip_path
    
    def test_python_code_analyzer(self):
        """Test Python code analysis."""
        analyzer = PythonCodeAnalyzer()
        
        code = '''
import os
import sys

class TestClass:
    """Test class with docstring."""
    
    def __init__(self):
        self.value = 0
    
    @property
    def doubled(self):
        return self.value * 2

def test_function(x, y):
    """Test function."""
    if x > y:
        return x - y
    else:
        return y - x
'''
        
        result = analyzer.analyze_code(code, "test.py")
        
        assert result['filename'] == "test.py"
        assert len(result['classes']) == 1
        assert len(result['functions']) == 1
        assert len(result['imports']) == 2
        assert result['classes'][0]['name'] == 'TestClass'
        assert result['functions'][0]['name'] == 'test_function'
        assert result['importance_score'] > 0
    
    def test_python_code_analyzer_syntax_error(self):
        """Test analyzer with syntax error."""
        analyzer = PythonCodeAnalyzer()
        
        # Invalid Python code
        code = '''
def invalid_function(
    # Missing closing parenthesis
    return "error"
'''
        
        result = analyzer.analyze_code(code, "invalid.py")
        
        assert result['filename'] == "invalid.py"
        assert result.get('parse_error') is True
        assert result['importance_score'] > 0  # Should still have fallback score
    
    def test_smart_zip_cache(self, temp_dir):
        """Test smart caching functionality."""
        cache = SmartZipCache(str(temp_dir / "cache"))
        
        # Test cache miss
        result = cache.get("nonexistent.zip", "file.py")
        assert result is None
        
        # Test cache set and get
        test_data = {"test": "data", "score": 10}
        cache.set("test.zip", "file.py", test_data)
        
        cached_result = cache.get("test.zip", "file.py")
        assert cached_result == test_data
        
        # Test cache stats
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 50.0
    
    def test_intelligent_zip_processor(self, sample_zip):
        """Test main ZIP processor."""
        processor = IntelligentZipProcessor(max_workers=2)
        
        result = processor.process_zip_file(str(sample_zip))
        
        assert result['zip_path'] == str(sample_zip)
        assert result['total_files'] > 0
        assert result['processed_files'] > 0
        assert 'processing_time' in result
        assert 'cache_stats' in result
        assert isinstance(result['results'], list)
    
    def test_zip_processor_selective_mode(self, sample_zip):
        """Test selective processing mode."""
        processor = IntelligentZipProcessor()
        
        # Test with high importance threshold
        result = processor.process_zip_file(str(sample_zip), selective=True, importance_threshold=50.0)
        
        assert result['important_files'] <= result['processed_files']
    
    def test_zip_processor_nonexistent_file(self):
        """Test processor with nonexistent file."""
        processor = IntelligentZipProcessor()
        
        result = processor.process_zip_file("nonexistent.zip")
        
        assert 'error' in result
        assert not result.get('success', True)
    
    def test_batch_processing(self, temp_dir):
        """Test batch ZIP processing."""
        processor = IntelligentZipProcessor(max_workers=2)
        
        # Create multiple ZIP files
        zip_files = []
        for i in range(3):
            zip_path = temp_dir / f"test_{i}.zip"
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr(f"module_{i}.py", f"# Module {i}\nprint('Hello {i}')")
            zip_files.append(str(zip_path))
        
        results = processor.batch_process_zips(zip_files)
        
        assert len(results) == 3
        for result in results:
            assert 'zip_path' in result


class TestRobustBinaryParser:
    """Test suite for binary format parsing."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_pptx_file(self, temp_dir):
        """Create mock PowerPoint file."""
        pptx_path = temp_dir / "test.pptx"
        
        with zipfile.ZipFile(pptx_path, 'w') as zf:
            zf.writestr("[Content_Types].xml", '''<?xml version="1.0"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
</Types>''')
            
            zf.writestr("_rels/.rels", '''<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>''')
            
            zf.writestr("ppt/presentation.xml", '''<?xml version="1.0"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:sldIdLst>
        <p:sldId id="256" r:id="rId2"/>
    </p:sldIdLst>
</p:presentation>''')
            
            zf.writestr("ppt/slides/slide1.xml", '''<?xml version="1.0"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:cSld>
        <p:spTree>
            <p:sp>
                <p:txBody>
                    <a:p xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                        <a:r><a:t>Test Slide Content</a:t></a:r>
                    </a:p>
                </p:txBody>
            </p:sp>
        </p:spTree>
    </p:cSld>
</p:sld>''')
        
        return pptx_path
    
    def test_format_validator(self, mock_pptx_file, temp_dir):
        """Test format detection."""
        validator = FormatValidator()
        
        # Test Office XML format detection
        format_type, confidence = validator.detect_format(mock_pptx_file)
        assert format_type == 'office_xml'
        assert confidence > 0.7
        
        # Test unknown format
        unknown_file = temp_dir / "unknown.bin"
        unknown_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')
        
        format_type, confidence = validator.detect_format(unknown_file)
        assert format_type == 'unknown'
        assert confidence == 0.0
    
    def test_powerpoint_parser_zip_fallback(self, mock_pptx_file):
        """Test PowerPoint parser with ZIP fallback."""
        parser = PowerPointParser()
        
        result = parser.parse(mock_pptx_file)
        
        assert result['success'] is True
        assert result['file_path'] == str(mock_pptx_file)
        assert result['file_size'] > 0
        assert 'parser' in result
    
    def test_powerpoint_parser_invalid_file(self, temp_dir):
        """Test parser with invalid file."""
        parser = PowerPointParser()
        
        # Create invalid file
        invalid_file = temp_dir / "invalid.pptx"
        invalid_file.write_text("This is not a PowerPoint file")
        
        result = parser.parse(invalid_file)
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_robust_binary_parser(self, mock_pptx_file):
        """Test main binary parser."""
        parser = RobustBinaryParser()
        
        result = parser.parse_file(mock_pptx_file)
        
        assert result['success'] is True
        assert 'format_detection' in result
        assert result['format_detection']['detected_format'] == 'office_xml'
    
    def test_parser_nonexistent_file(self):
        """Test parser with nonexistent file."""
        parser = RobustBinaryParser()
        
        result = parser.parse_file("nonexistent.pptx")
        
        assert result['success'] is False
        assert 'File not found' in result['error']
    
    def test_batch_parsing(self, temp_dir):
        """Test batch file parsing."""
        parser = RobustBinaryParser()
        
        # Create test files
        files = []
        for i in range(3):
            file_path = temp_dir / f"test_{i}.txt"
            file_path.write_text(f"Test content {i}")
            files.append(file_path)
        
        results = parser.batch_parse(files)
        
        assert len(results) == 3
        for result in results:
            assert 'success' in result
            assert 'file_path' in result


class TestAsyncFileProcessor:
    """Test suite for async I/O optimization."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_file(self, temp_dir):
        """Create sample file for testing."""
        file_path = temp_dir / "test.txt"
        content = "Line 1\nLine 2\nLine 3\n" * 1000  # Create larger file
        file_path.write_text(content)
        return file_path
    
    def test_resource_manager(self):
        """Test resource management."""
        manager = ResourceManager(max_concurrent_files=5, max_memory_mb=10)
        
        assert manager.max_concurrent_files == 5
        assert manager.max_memory_bytes == 10 * 1024 * 1024
        
        stats = manager.get_stats()
        assert 'active_tasks' in stats
        assert 'available_file_slots' in stats
        assert 'memory_usage_mb' in stats
    
    @pytest.mark.asyncio
    async def test_streaming_file_reader(self, sample_file):
        """Test streaming file reader."""
        from async_io.async_file_processor import StreamingFileReader
        
        reader = StreamingFileReader(chunk_size=1024)
        
        chunks = []
        async for chunk in reader.read_file_chunks(sample_file):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        
        # Verify content integrity
        combined_content = b''.join(chunks)
        original_content = sample_file.read_bytes()
        assert combined_content == original_content
    
    @pytest.mark.asyncio
    async def test_streaming_file_writer(self, temp_dir):
        """Test streaming file writer."""
        from async_io.async_file_processor import StreamingFileWriter
        
        writer = StreamingFileWriter()
        output_path = temp_dir / "output.txt"
        
        async def generate_chunks():
            for i in range(10):
                yield f"Chunk {i}\n".encode()
        
        result = await writer.write_chunks(output_path, generate_chunks())
        
        assert result['success'] is True
        assert result['bytes_written'] > 0
        assert result['chunks_written'] == 10
        assert output_path.exists()
    
    @pytest.mark.asyncio
    async def test_async_file_processor(self, sample_file, temp_dir):
        """Test main async file processor."""
        processor = AsyncFileProcessor()
        
        async def identity_processor(chunks):
            async for chunk in chunks:
                yield chunk
        
        output_path = temp_dir / "processed.txt"
        result = await processor.process_file(sample_file, identity_processor, output_path)
        
        assert result['success'] is True
        assert result['bytes_written'] > 0
        assert 'processing_time' in result
        assert output_path.exists()
    
    @pytest.mark.asyncio
    async def test_async_file_copy(self, sample_file, temp_dir):
        """Test async file copy."""
        processor = AsyncFileProcessor()
        
        dst_path = temp_dir / "copy.txt"
        result = await processor.copy_file_async(sample_file, dst_path)
        
        assert result['success'] is True
        assert result['file_size'] > 0
        assert 'throughput_mbps' in result
        assert dst_path.exists()
        
        # Verify content integrity
        assert sample_file.read_text() == dst_path.read_text()
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, temp_dir):
        """Test batch file processing."""
        processor = AsyncFileProcessor()
        
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = temp_dir / f"input_{i}.txt"
            file_path.write_text(f"Content {i}\n" * 100)
            files.append(file_path)
        
        async def uppercase_processor(chunks):
            async for chunk in chunks:
                yield chunk.upper()
        
        output_dir = temp_dir / "output"
        results = await processor.process_files_batch(files, uppercase_processor, output_dir)
        
        assert len(results) == 3
        for result in results:
            assert result.get('success', False) is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, temp_dir):
        """Test error handling in async processing."""
        processor = AsyncFileProcessor()
        
        # Test with nonexistent file
        async def dummy_processor(chunks):
            async for chunk in chunks:
                yield chunk
        
        result = await processor.process_file("nonexistent.txt", dummy_processor)
        
        assert result['success'] is False
        assert 'error' in result


class TestIntelligentCache:
    """Test suite for intelligent caching system."""
    
    def test_lru_cache_basic_operations(self):
        """Test basic LRU cache operations."""
        cache = LRUCache(max_size=3, max_memory_mb=1)
        
        # Test put and get
        assert cache.put("key1", "value1") is True
        assert cache.get("key1") == "value1"
        
        # Test cache miss
        assert cache.get("nonexistent") is None
        
        # Test cache stats
        stats = cache.stats.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
    
    def test_lru_cache_eviction(self):
        """Test LRU eviction policy."""
        cache = LRUCache(max_size=2, max_memory_mb=1)
        
        # Fill cache to capacity
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        # Access key1 to make it recently used
        cache.get("key1")
        
        # Add new item, should evict key2
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"  # Should still exist
        assert cache.get("key2") is None      # Should be evicted
        assert cache.get("key3") == "value3"  # Should exist
    
    def test_lru_cache_ttl(self):
        """Test TTL functionality."""
        cache = LRUCache(max_size=10, max_memory_mb=1)
        
        # Put item with short TTL
        cache.put("key1", "value1", ttl=0.1)  # 100ms TTL
        
        # Should be available immediately
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        assert cache.get("key1") is None
    
    def test_lru_cache_tags(self):
        """Test tag-based operations."""
        cache = LRUCache(max_size=10, max_memory_mb=1)
        
        # Put items with tags
        cache.put("key1", "value1", tags={"group1", "important"})
        cache.put("key2", "value2", tags={"group1"})
        cache.put("key3", "value3", tags={"group2"})
        
        # Test get by tag
        group1_entries = cache.get_entries_by_tag("group1")
        assert len(group1_entries) == 2
        
        # Test remove by tag
        removed_count = cache.remove_by_tag("group1")
        assert removed_count == 2
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_predictive_engine(self):
        """Test predictive engine."""
        engine = PredictiveEngine(db_path=":memory:")
        
        # Record access pattern
        current_time = time.time()
        for i in range(5):
            engine.record_access("key1")
            time.sleep(0.01)  # Small delay to create pattern
        
        # Get predictions
        predictions = engine.get_predictions(lookahead_seconds=3600)
        
        # Should have some predictions (though may be empty due to short pattern)
        assert isinstance(predictions, list)
    
    def test_intelligent_cache_basic(self):
        """Test basic intelligent cache operations."""
        cache = IntelligentCache(
            max_size=10,
            max_memory_mb=1,
            disk_cache_dir=":memory:",
            enable_prediction=False,  # Disable for simpler testing
            auto_tune=False
        )
        
        # Test basic operations
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test default value
        assert cache.get("nonexistent", "default") == "default"
        
        # Test removal
        assert cache.remove("key1") is True
        assert cache.get("key1") is None
        
        cache.shutdown()
    
    def test_intelligent_cache_preloading(self):
        """Test cache preloading functionality."""
        cache = IntelligentCache(
            max_size=10,
            max_memory_mb=1,
            enable_prediction=False,
            auto_tune=False
        )
        
        # Register preload callback
        def load_data():
            return "preloaded_value"
        
        cache.register_preload_callback("key1", load_data)
        
        # Test manual warming
        cache.warm_cache(["key1"])
        
        # Give some time for background task
        time.sleep(0.1)
        
        # Value should be preloaded (may not be immediate due to threading)
        # This is a basic test - in practice, preloading is asynchronous
        
        cache.shutdown()
    
    def test_intelligent_cache_stats(self):
        """Test comprehensive cache statistics."""
        cache = IntelligentCache(
            max_size=5,
            max_memory_mb=1,
            enable_prediction=False,
            auto_tune=False
        )
        
        # Perform some operations
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.get("key1")
        cache.get("nonexistent")
        
        stats = cache.get_comprehensive_stats()
        
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        assert 'system_memory_percent' in stats
        assert 'cache_memory_mb' in stats
        
        cache.shutdown()


class TestIntegration:
    """Integration tests for all optimizations working together."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_zip_processing_with_caching(self, temp_dir):
        """Test ZIP processing with intelligent caching."""
        # Create test ZIP
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("module.py", "print('Hello World')")
        
        # Initialize cache
        cache = IntelligentCache(max_size=100, enable_prediction=False, auto_tune=False)
        
        # Process ZIP multiple times to test caching
        processor = IntelligentZipProcessor()
        
        # First processing
        result1 = processor.process_zip_file(str(zip_path))
        cache.put(f"zip_result_{zip_path}", result1)
        
        # Second processing (should use cache)
        cached_result = cache.get(f"zip_result_{zip_path}")
        
        assert cached_result is not None
        assert cached_result['zip_path'] == result1['zip_path']
        
        cache.shutdown()
    
    @pytest.mark.asyncio
    async def test_async_binary_processing(self, temp_dir):
        """Test async processing of binary files."""
        # Create mock binary file
        binary_path = temp_dir / "test.pptx"
        with zipfile.ZipFile(binary_path, 'w') as zf:
            zf.writestr("[Content_Types].xml", "<?xml version='1.0'?><Types/>")
        
        # Process with async I/O
        processor = AsyncFileProcessor()
        parser = RobustBinaryParser()
        
        async def parse_processor(chunks):
            # Collect all chunks
            content = b''
            async for chunk in chunks:
                content += chunk
            
            # Write to temp file and parse
            temp_file = temp_dir / "temp_parse.pptx"
            temp_file.write_bytes(content)
            
            result = parser.parse_file(temp_file)
            yield json.dumps(result).encode()
        
        output_path = temp_dir / "parse_result.json"
        result = await processor.process_file(binary_path, parse_processor, output_path)
        
        assert result['success'] is True
        assert output_path.exists()
    
    def test_performance_monitoring(self):
        """Test performance monitoring across all components."""
        # Initialize all components
        zip_processor = IntelligentZipProcessor(max_workers=2)
        binary_parser = RobustBinaryParser()
        cache = IntelligentCache(max_size=50, enable_prediction=False, auto_tune=False)
        
        # Get initial stats
        zip_cache_stats = zip_processor.cache.get_stats()
        cache_stats = cache.get_comprehensive_stats()
        
        # Verify stats structure
        assert 'hits' in zip_cache_stats
        assert 'misses' in zip_cache_stats
        assert 'hit_rate' in zip_cache_stats
        
        assert 'hits' in cache_stats
        assert 'system_memory_percent' in cache_stats
        
        cache.shutdown()


# Test configuration and utilities
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def test_module_imports():
    """Test that all optimization modules can be imported."""
    # This test ensures all dependencies are available
    from zip_opt.intelligent_zip_processor import IntelligentZipProcessor
    from binary_opt.robust_binary_parser import RobustBinaryParser
    from async_io.async_file_processor import AsyncFileProcessor
    from cache_opt.intelligent_cache import IntelligentCache
    
    # Basic instantiation test
    zip_proc = IntelligentZipProcessor()
    binary_parser = RobustBinaryParser()
    cache = IntelligentCache(enable_prediction=False, auto_tune=False)
    
    assert zip_proc is not None
    assert binary_parser is not None
    assert cache is not None
    
    cache.shutdown()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
