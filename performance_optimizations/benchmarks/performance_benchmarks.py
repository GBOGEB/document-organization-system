"""
Performance Benchmarking Suite
Comprehensive benchmarks for all optimization modules with before/after comparisons.
"""

import asyncio
import csv
import json
import logging
import os
import random
import shutil
import string
import tempfile
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Tuple
import psutil
import matplotlib.pyplot as plt
import pandas as pd

# Import optimization modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from zip_opt.intelligent_zip_processor import IntelligentZipProcessor
from binary_opt.robust_binary_parser import RobustBinaryParser
from async_io.async_file_processor import AsyncFileProcessor, ResourceManager
from cache_opt.intelligent_cache import IntelligentCache


class BenchmarkResult:
    """Container for benchmark results."""
    
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.metrics = {}
        self.start_time = None
        self.end_time = None
        self.memory_before = None
        self.memory_after = None
        self.cpu_before = None
        self.cpu_after = None
    
    def start(self):
        """Start timing and resource monitoring."""
        self.start_time = time.perf_counter()
        self.memory_before = psutil.virtual_memory().percent
        self.cpu_before = psutil.cpu_percent()
    
    def end(self):
        """End timing and resource monitoring."""
        self.end_time = time.perf_counter()
        self.memory_after = psutil.virtual_memory().percent
        self.cpu_after = psutil.cpu_percent()
        
        self.metrics['execution_time'] = self.end_time - self.start_time
        self.metrics['memory_delta'] = self.memory_after - self.memory_before
        self.metrics['cpu_delta'] = self.cpu_after - self.cpu_before
    
    def add_metric(self, key: str, value: Any):
        """Add custom metric."""
        self.metrics[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'category': self.category,
            'execution_time': self.metrics.get('execution_time', 0),
            'memory_delta': self.metrics.get('memory_delta', 0),
            'cpu_delta': self.metrics.get('cpu_delta', 0),
            **self.metrics
        }


class TestDataGenerator:
    """Generate test data for benchmarking."""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_python_files(self, count: int = 50, size_range: Tuple[int, int] = (1000, 10000)) -> List[Path]:
        """Create Python test files."""
        files = []
        
        for i in range(count):
            file_path = self.temp_dir / f"test_file_{i}.py"
            
            # Generate Python code with varying complexity
            lines = []
            lines.append("#!/usr/bin/env python3")
            lines.append('"""Test Python file for benchmarking."""')
            lines.append("")
            lines.append("import os")
            lines.append("import sys")
            lines.append("import json")
            lines.append("")
            
            # Add classes
            for j in range(random.randint(1, 5)):
                lines.append(f"class TestClass{j}:")
                lines.append(f'    """Test class {j}."""')
                lines.append("")
                lines.append("    def __init__(self):")
                lines.append("        self.value = 0")
                lines.append("")
                
                # Add methods
                for k in range(random.randint(2, 8)):
                    lines.append(f"    def method_{k}(self, param):")
                    lines.append(f'        """Method {k}."""')
                    lines.append("        if param > 0:")
                    lines.append("            return param * 2")
                    lines.append("        else:")
                    lines.append("            return 0")
                    lines.append("")
            
            # Add functions
            for j in range(random.randint(3, 10)):
                lines.append(f"def function_{j}(x, y):")
                lines.append(f'    """Function {j}."""')
                lines.append("    result = 0")
                lines.append("    for i in range(x):")
                lines.append("        if i % 2 == 0:")
                lines.append("            result += y")
                lines.append("        else:")
                lines.append("            result -= y")
                lines.append("    return result")
                lines.append("")
            
            # Pad to desired size
            content = "\n".join(lines)
            min_size, max_size = size_range
            target_size = random.randint(min_size, max_size)
            
            while len(content) < target_size:
                content += f"\n# Padding comment {len(content)}"
            
            file_path.write_text(content)
            files.append(file_path)
        
        return files
    
    def create_zip_files(self, count: int = 10, files_per_zip: int = 20) -> List[Path]:
        """Create ZIP files containing Python files."""
        zip_files = []
        
        for i in range(count):
            zip_path = self.temp_dir / f"test_archive_{i}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Create Python files in memory and add to ZIP
                for j in range(files_per_zip):
                    file_name = f"module_{j}.py"
                    content = self._generate_python_content(f"Module{j}")
                    zf.writestr(file_name, content)
                
                # Add some non-Python files
                zf.writestr("README.md", "# Test Project\nThis is a test project.")
                zf.writestr("requirements.txt", "requests>=2.25.0\nnumpy>=1.20.0")
                zf.writestr("config.json", '{"debug": true, "version": "1.0.0"}')
            
            zip_files.append(zip_path)
        
        return zip_files
    
    def create_binary_files(self, count: int = 20) -> List[Path]:
        """Create mock binary files for testing."""
        files = []
        
        for i in range(count):
            # Create mock PowerPoint file (ZIP with specific structure)
            pptx_path = self.temp_dir / f"presentation_{i}.pptx"
            
            with zipfile.ZipFile(pptx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add PowerPoint-like structure
                zf.writestr("[Content_Types].xml", self._get_content_types_xml())
                zf.writestr("_rels/.rels", self._get_rels_xml())
                zf.writestr("ppt/presentation.xml", self._get_presentation_xml())
                
                # Add slides
                for j in range(random.randint(3, 10)):
                    slide_xml = self._get_slide_xml(j + 1)
                    zf.writestr(f"ppt/slides/slide{j + 1}.xml", slide_xml)
                
                # Add theme and layout files
                zf.writestr("ppt/theme/theme1.xml", self._get_theme_xml())
                zf.writestr("ppt/slideLayouts/slideLayout1.xml", self._get_layout_xml())
            
            files.append(pptx_path)
        
        return files
    
    def create_large_files(self, count: int = 5, size_mb: int = 10) -> List[Path]:
        """Create large files for I/O testing."""
        files = []
        
        for i in range(count):
            file_path = self.temp_dir / f"large_file_{i}.txt"
            
            # Generate content
            lines = []
            target_size = size_mb * 1024 * 1024
            
            while len("\n".join(lines).encode()) < target_size:
                line = f"Line {len(lines)}: " + "".join(random.choices(string.ascii_letters + string.digits, k=80))
                lines.append(line)
            
            file_path.write_text("\n".join(lines))
            files.append(file_path)
        
        return files
    
    def _generate_python_content(self, class_name: str) -> str:
        """Generate Python file content."""
        return f'''#!/usr/bin/env python3
"""
{class_name} module for testing.
"""

import os
import sys
from typing import Any, Dict, List, Optional


class {class_name}:
    """Test class {class_name}."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.data = {{}}
        self.counter = 0
    
    def process_data(self, items: List[Any]) -> Dict[str, Any]:
        """Process data items."""
        result = {{"processed": [], "errors": []}}
        
        for item in items:
            try:
                if isinstance(item, (int, float)):
                    processed = item * 2 + 1
                elif isinstance(item, str):
                    processed = item.upper()
                else:
                    processed = str(item)
                
                result["processed"].append(processed)
                self.counter += 1
                
            except Exception as e:
                result["errors"].append(str(e))
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {{
            "name": self.name,
            "counter": self.counter,
            "data_size": len(self.data)
        }}


def utility_function(x: int, y: int) -> int:
    """Utility function for testing."""
    if x > y:
        return x - y
    elif x < y:
        return y - x
    else:
        return x + y


def main():
    """Main function."""
    processor = {class_name}("test")
    test_data = list(range(100))
    result = processor.process_data(test_data)
    print(f"Processed {{len(result['processed'])}} items")


if __name__ == "__main__":
    main()
'''
    
    def _get_content_types_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-presentationml.presentation.main+xml"/>
</Types>'''
    
    def _get_rels_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>'''
    
    def _get_presentation_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:sldMasterIdLst>
        <p:sldMasterId id="2147483648" r:id="rId1"/>
    </p:sldMasterIdLst>
    <p:sldIdLst>
        <p:sldId id="256" r:id="rId2"/>
    </p:sldIdLst>
    <p:sldSz cx="9144000" cy="6858000" type="screen4x3"/>
</p:presentation>'''
    
    def _get_slide_xml(self, slide_num: int) -> str:
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:cSld>
        <p:spTree>
            <p:sp>
                <p:txBody>
                    <a:p xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                        <a:r>
                            <a:t>Slide {slide_num} Content</a:t>
                        </a:r>
                    </a:p>
                </p:txBody>
            </p:sp>
        </p:spTree>
    </p:cSld>
</p:sld>'''
    
    def _get_theme_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
    <a:themeElements>
        <a:clrScheme name="Office">
            <a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
            <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
        </a:clrScheme>
    </a:themeElements>
</a:theme>'''
    
    def _get_layout_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:cSld name="Title Slide">
        <p:spTree>
            <p:sp>
                <p:txBody>
                    <a:p xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                        <a:endParaRPr lang="en-US"/>
                    </a:p>
                </p:txBody>
            </p:sp>
        </p:spTree>
    </p:cSld>
</p:sldLayout>'''


class PerformanceBenchmarks:
    """Main benchmarking class."""
    
    def __init__(self, output_dir: str = "./benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.temp_dir = tempfile.mkdtemp(prefix="perf_bench_")
        self.data_generator = TestDataGenerator(self.temp_dir)
        
        self.results = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize test data
        self._setup_test_data()
    
    def _setup_test_data(self):
        """Set up test data for benchmarks."""
        self.logger.info("Setting up test data...")
        
        self.python_files = self.data_generator.create_python_files(50)
        self.zip_files = self.data_generator.create_zip_files(10)
        self.binary_files = self.data_generator.create_binary_files(20)
        self.large_files = self.data_generator.create_large_files(5, 10)
        
        self.logger.info(f"Created {len(self.python_files)} Python files")
        self.logger.info(f"Created {len(self.zip_files)} ZIP files")
        self.logger.info(f"Created {len(self.binary_files)} binary files")
        self.logger.info(f"Created {len(self.large_files)} large files")
    
    def benchmark_zip_processing(self) -> List[BenchmarkResult]:
        """Benchmark ZIP processing optimization."""
        results = []
        
        # Baseline: Simple ZIP processing
        baseline_result = BenchmarkResult("ZIP Processing - Baseline", "ZIP Processing")
        baseline_result.start()
        
        baseline_count = 0
        for zip_path in self.zip_files[:5]:  # Test subset
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    for file_info in zf.filelist:
                        if file_info.filename.endswith('.py'):
                            content = zf.read(file_info.filename)
                            # Simple text analysis
                            lines = content.decode('utf-8', errors='ignore').splitlines()
                            baseline_count += len(lines)
            except Exception as e:
                self.logger.error(f"Baseline ZIP processing error: {e}")
        
        baseline_result.end()
        baseline_result.add_metric('files_processed', baseline_count)
        baseline_result.add_metric('throughput_files_per_sec', baseline_count / baseline_result.metrics['execution_time'])
        results.append(baseline_result)
        
        # Optimized: Intelligent ZIP processing
        optimized_result = BenchmarkResult("ZIP Processing - Optimized", "ZIP Processing")
        optimized_result.start()
        
        processor = IntelligentZipProcessor(max_workers=4)
        optimized_count = 0
        
        for zip_path in self.zip_files[:5]:
            try:
                result = processor.process_zip_file(str(zip_path), selective=True, importance_threshold=1.0)
                if result.get('results'):
                    optimized_count += len(result['results'])
            except Exception as e:
                self.logger.error(f"Optimized ZIP processing error: {e}")
        
        optimized_result.end()
        optimized_result.add_metric('files_processed', optimized_count)
        optimized_result.add_metric('throughput_files_per_sec', optimized_count / optimized_result.metrics['execution_time'])
        optimized_result.add_metric('cache_hit_rate', processor.cache.get_stats()['hit_rate'])
        results.append(optimized_result)
        
        return results
    
    def benchmark_binary_parsing(self) -> List[BenchmarkResult]:
        """Benchmark binary format parsing."""
        results = []
        
        # Baseline: Simple binary file reading
        baseline_result = BenchmarkResult("Binary Parsing - Baseline", "Binary Parsing")
        baseline_result.start()
        
        baseline_count = 0
        baseline_errors = 0
        
        for file_path in self.binary_files[:10]:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    baseline_count += len(content)
            except Exception as e:
                baseline_errors += 1
                self.logger.error(f"Baseline binary parsing error: {e}")
        
        baseline_result.end()
        baseline_result.add_metric('bytes_processed', baseline_count)
        baseline_result.add_metric('files_processed', len(self.binary_files[:10]) - baseline_errors)
        baseline_result.add_metric('error_rate', baseline_errors / len(self.binary_files[:10]) * 100)
        results.append(baseline_result)
        
        # Optimized: Robust binary parser
        optimized_result = BenchmarkResult("Binary Parsing - Optimized", "Binary Parsing")
        optimized_result.start()
        
        parser = RobustBinaryParser()
        optimized_count = 0
        optimized_errors = 0
        successful_parses = 0
        
        for file_path in self.binary_files[:10]:
            try:
                result = parser.parse_file(file_path)
                if result.get('success'):
                    successful_parses += 1
                    optimized_count += result.get('file_size', 0)
                else:
                    optimized_errors += 1
            except Exception as e:
                optimized_errors += 1
                self.logger.error(f"Optimized binary parsing error: {e}")
        
        optimized_result.end()
        optimized_result.add_metric('bytes_processed', optimized_count)
        optimized_result.add_metric('files_processed', successful_parses)
        optimized_result.add_metric('error_rate', optimized_errors / len(self.binary_files[:10]) * 100)
        optimized_result.add_metric('success_rate', successful_parses / len(self.binary_files[:10]) * 100)
        results.append(optimized_result)
        
        return results
    
    def benchmark_async_io(self) -> List[BenchmarkResult]:
        """Benchmark async I/O performance."""
        results = []
        
        # Baseline: Synchronous file processing
        baseline_result = BenchmarkResult("File I/O - Synchronous", "Async I/O")
        baseline_result.start()
        
        baseline_bytes = 0
        output_dir = Path(self.temp_dir) / "sync_output"
        output_dir.mkdir(exist_ok=True)
        
        for file_path in self.large_files[:3]:
            try:
                with open(file_path, 'rb') as src:
                    content = src.read()
                    baseline_bytes += len(content)
                
                output_path = output_dir / file_path.name
                with open(output_path, 'wb') as dst:
                    dst.write(content.upper() if content.decode('utf-8', errors='ignore') else content)
            except Exception as e:
                self.logger.error(f"Sync I/O error: {e}")
        
        baseline_result.end()
        baseline_result.add_metric('bytes_processed', baseline_bytes)
        baseline_result.add_metric('throughput_mbps', (baseline_bytes / (1024 * 1024)) / baseline_result.metrics['execution_time'])
        results.append(baseline_result)
        
        # Optimized: Asynchronous file processing
        async def async_benchmark():
            optimized_result = BenchmarkResult("File I/O - Asynchronous", "Async I/O")
            optimized_result.start()
            
            resource_manager = ResourceManager(max_concurrent_files=10)
            processor = AsyncFileProcessor(resource_manager)
            
            async def uppercase_processor(chunks):
                async for chunk in chunks:
                    try:
                        text = chunk.decode('utf-8')
                        yield text.upper().encode('utf-8')
                    except UnicodeDecodeError:
                        yield chunk
            
            output_dir = Path(self.temp_dir) / "async_output"
            output_dir.mkdir(exist_ok=True)
            
            tasks = []
            for file_path in self.large_files[:3]:
                output_path = output_dir / file_path.name
                task = processor.process_file(file_path, uppercase_processor, output_path)
                tasks.append(task)
            
            results_async = await asyncio.gather(*tasks)
            
            optimized_result.end()
            
            total_bytes = sum(r.get('bytes_written', 0) for r in results_async if r.get('success'))
            optimized_result.add_metric('bytes_processed', total_bytes)
            optimized_result.add_metric('throughput_mbps', (total_bytes / (1024 * 1024)) / optimized_result.metrics['execution_time'])
            optimized_result.add_metric('concurrent_files', len(self.large_files[:3]))
            
            return optimized_result
        
        # Run async benchmark
        optimized_result = asyncio.run(async_benchmark())
        results.append(optimized_result)
        
        return results
    
    def benchmark_caching(self) -> List[BenchmarkResult]:
        """Benchmark caching system performance."""
        results = []
        
        # Baseline: No caching
        baseline_result = BenchmarkResult("Caching - No Cache", "Caching")
        baseline_result.start()
        
        def expensive_operation(key: str) -> str:
            """Simulate expensive operation."""
            time.sleep(0.01)  # 10ms delay
            return f"result_for_{key}"
        
        baseline_operations = 0
        test_keys = [f"key_{i}" for i in range(100)]
        
        # Simulate repeated access pattern
        for _ in range(3):  # 3 rounds
            for key in test_keys:
                result = expensive_operation(key)
                baseline_operations += 1
        
        baseline_result.end()
        baseline_result.add_metric('operations', baseline_operations)
        baseline_result.add_metric('ops_per_second', baseline_operations / baseline_result.metrics['execution_time'])
        results.append(baseline_result)
        
        # Optimized: With intelligent caching
        optimized_result = BenchmarkResult("Caching - Intelligent Cache", "Caching")
        optimized_result.start()
        
        cache = IntelligentCache(max_size=200, enable_prediction=True, auto_tune=False)
        
        # Register preload callbacks
        for key in test_keys:
            cache.register_preload_callback(key, lambda k=key: expensive_operation(k))
        
        optimized_operations = 0
        cache_hits = 0
        
        # Simulate repeated access pattern
        for _ in range(3):  # 3 rounds
            for key in test_keys:
                result = cache.get(key)
                if result is None:
                    result = expensive_operation(key)
                    cache.put(key, result, ttl=3600)
                    optimized_operations += 1
                else:
                    cache_hits += 1
        
        optimized_result.end()
        
        cache_stats = cache.get_comprehensive_stats()
        optimized_result.add_metric('operations', optimized_operations)
        optimized_result.add_metric('cache_hits', cache_hits)
        optimized_result.add_metric('hit_rate', cache_stats['hit_rate'])
        optimized_result.add_metric('ops_per_second', (optimized_operations + cache_hits) / optimized_result.metrics['execution_time'])
        
        cache.shutdown()
        results.append(optimized_result)
        
        return results
    
    def run_all_benchmarks(self) -> Dict[str, List[BenchmarkResult]]:
        """Run all benchmarks and return results."""
        self.logger.info("Starting comprehensive performance benchmarks...")
        
        all_results = {}
        
        # Run ZIP processing benchmarks
        self.logger.info("Running ZIP processing benchmarks...")
        all_results['zip_processing'] = self.benchmark_zip_processing()
        
        # Run binary parsing benchmarks
        self.logger.info("Running binary parsing benchmarks...")
        all_results['binary_parsing'] = self.benchmark_binary_parsing()
        
        # Run async I/O benchmarks
        self.logger.info("Running async I/O benchmarks...")
        all_results['async_io'] = self.benchmark_async_io()
        
        # Run caching benchmarks
        self.logger.info("Running caching benchmarks...")
        all_results['caching'] = self.benchmark_caching()
        
        # Store all results
        self.results = []
        for category_results in all_results.values():
            self.results.extend(category_results)
        
        self.logger.info("All benchmarks completed!")
        return all_results
    
    def generate_reports(self, results: Dict[str, List[BenchmarkResult]]):
        """Generate comprehensive benchmark reports."""
        # Generate CSV report
        self._generate_csv_report(results)
        
        # Generate JSON report
        self._generate_json_report(results)
        
        # Generate markdown report
        self._generate_markdown_report(results)
        
        # Generate performance charts
        self._generate_charts(results)
    
    def _generate_csv_report(self, results: Dict[str, List[BenchmarkResult]]):
        """Generate CSV report."""
        csv_path = self.output_dir / "benchmark_results.csv"
        
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['category', 'name', 'execution_time', 'memory_delta', 'cpu_delta']
            
            # Get all unique metric keys
            all_metrics = set()
            for category_results in results.values():
                for result in category_results:
                    all_metrics.update(result.metrics.keys())
            
            fieldnames.extend(sorted(all_metrics - {'execution_time', 'memory_delta', 'cpu_delta'}))
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for category_results in results.values():
                for result in category_results:
                    row = result.to_dict()
                    writer.writerow(row)
        
        self.logger.info(f"CSV report saved to {csv_path}")
    
    def _generate_json_report(self, results: Dict[str, List[BenchmarkResult]]):
        """Generate JSON report."""
        json_path = self.output_dir / "benchmark_results.json"
        
        json_data = {}
        for category, category_results in results.items():
            json_data[category] = [result.to_dict() for result in category_results]
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        self.logger.info(f"JSON report saved to {json_path}")
    
    def _generate_markdown_report(self, results: Dict[str, List[BenchmarkResult]]):
        """Generate markdown report."""
        md_path = self.output_dir / "benchmark_report.md"
        
        with open(md_path, 'w') as f:
            f.write("# Performance Optimization Benchmark Results\n\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary table
            f.write("## Summary\n\n")
            f.write("| Category | Baseline Time (s) | Optimized Time (s) | Improvement | Key Metrics |\n")
            f.write("|----------|-------------------|-------------------|-------------|-------------|\n")
            
            for category, category_results in results.items():
                if len(category_results) >= 2:
                    baseline = category_results[0]
                    optimized = category_results[1]
                    
                    baseline_time = baseline.metrics.get('execution_time', 0)
                    optimized_time = optimized.metrics.get('execution_time', 0)
                    
                    if baseline_time > 0:
                        improvement = ((baseline_time - optimized_time) / baseline_time) * 100
                        improvement_str = f"{improvement:.1f}%"
                    else:
                        improvement_str = "N/A"
                    
                    # Key metrics
                    key_metrics = []
                    if 'hit_rate' in optimized.metrics:
                        key_metrics.append(f"Hit Rate: {optimized.metrics['hit_rate']:.1f}%")
                    if 'throughput_mbps' in optimized.metrics:
                        key_metrics.append(f"Throughput: {optimized.metrics['throughput_mbps']:.1f} MB/s")
                    if 'success_rate' in optimized.metrics:
                        key_metrics.append(f"Success: {optimized.metrics['success_rate']:.1f}%")
                    
                    f.write(f"| {category.replace('_', ' ').title()} | {baseline_time:.3f} | {optimized_time:.3f} | {improvement_str} | {', '.join(key_metrics)} |\n")
            
            f.write("\n")
            
            # Detailed results
            for category, category_results in results.items():
                f.write(f"## {category.replace('_', ' ').title()}\n\n")
                
                for result in category_results:
                    f.write(f"### {result.name}\n\n")
                    f.write(f"- **Execution Time**: {result.metrics.get('execution_time', 0):.3f} seconds\n")
                    f.write(f"- **Memory Delta**: {result.metrics.get('memory_delta', 0):.1f}%\n")
                    f.write(f"- **CPU Delta**: {result.metrics.get('cpu_delta', 0):.1f}%\n")
                    
                    # Additional metrics
                    for key, value in result.metrics.items():
                        if key not in ['execution_time', 'memory_delta', 'cpu_delta']:
                            if isinstance(value, float):
                                f.write(f"- **{key.replace('_', ' ').title()}**: {value:.3f}\n")
                            else:
                                f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
                    
                    f.write("\n")
        
        self.logger.info(f"Markdown report saved to {md_path}")
    
    def _generate_charts(self, results: Dict[str, List[BenchmarkResult]]):
        """Generate performance charts."""
        try:
            # Execution time comparison
            categories = []
            baseline_times = []
            optimized_times = []
            
            for category, category_results in results.items():
                if len(category_results) >= 2:
                    categories.append(category.replace('_', ' ').title())
                    baseline_times.append(category_results[0].metrics.get('execution_time', 0))
                    optimized_times.append(category_results[1].metrics.get('execution_time', 0))
            
            if categories:
                fig, ax = plt.subplots(figsize=(12, 6))
                x = range(len(categories))
                width = 0.35
                
                ax.bar([i - width/2 for i in x], baseline_times, width, label='Baseline', alpha=0.8)
                ax.bar([i + width/2 for i in x], optimized_times, width, label='Optimized', alpha=0.8)
                
                ax.set_xlabel('Optimization Category')
                ax.set_ylabel('Execution Time (seconds)')
                ax.set_title('Performance Comparison: Baseline vs Optimized')
                ax.set_xticks(x)
                ax.set_xticklabels(categories, rotation=45, ha='right')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                plt.tight_layout()
                chart_path = self.output_dir / "performance_comparison.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                self.logger.info(f"Performance chart saved to {chart_path}")
        
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.temp_dir)
            self.logger.info("Temporary files cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up: {e}")


# Example usage and main execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run benchmarks
    benchmarks = PerformanceBenchmarks()
    
    try:
        results = benchmarks.run_all_benchmarks()
        benchmarks.generate_reports(results)
        
        print("\n" + "="*60)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*60)
        
        for category, category_results in results.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for result in category_results:
                exec_time = result.metrics.get('execution_time', 0)
                print(f"  {result.name}: {exec_time:.3f}s")
        
        print(f"\nDetailed reports saved to: {benchmarks.output_dir}")
        
    finally:
        benchmarks.cleanup()
