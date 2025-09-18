"""
Asynchronous I/O Implementation
High-performance async file processing with streaming and resource management.
"""

import asyncio
import aiofiles
import aiofiles.os
import logging
import mmap
import os
import time
from asyncio import Semaphore, Queue
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union
import psutil
import weakref


class ResourceManager:
    """Adaptive resource management for async operations."""
    
    def __init__(self, max_concurrent_files: Optional[int] = None, 
                 max_memory_mb: Optional[int] = None):
        self.cpu_count = os.cpu_count() or 4
        self.available_memory = psutil.virtual_memory().available
        
        # Adaptive limits based on system resources
        self.max_concurrent_files = max_concurrent_files or min(100, self.cpu_count * 8)
        self.max_memory_bytes = (max_memory_mb or 
                               min(1024, self.available_memory // (1024 * 1024) // 4)) * 1024 * 1024
        
        # Semaphores for resource control
        self.file_semaphore = Semaphore(self.max_concurrent_files)
        self.memory_semaphore = Semaphore(self.max_memory_bytes // (1024 * 1024))  # MB units
        
        # Monitoring
        self.active_tasks = weakref.WeakSet()
        self.memory_usage = 0
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"ResourceManager initialized: "
                        f"max_files={self.max_concurrent_files}, "
                        f"max_memory={self.max_memory_bytes // (1024*1024)}MB")
    
    async def acquire_file_slot(self):
        """Acquire a file processing slot."""
        await self.file_semaphore.acquire()
    
    def release_file_slot(self):
        """Release a file processing slot."""
        self.file_semaphore.release()
    
    async def acquire_memory(self, size_mb: int):
        """Acquire memory allocation."""
        slots_needed = max(1, size_mb)
        for _ in range(slots_needed):
            await self.memory_semaphore.acquire()
        self.memory_usage += size_mb * 1024 * 1024
    
    def release_memory(self, size_mb: int):
        """Release memory allocation."""
        slots_to_release = max(1, size_mb)
        for _ in range(slots_to_release):
            self.memory_semaphore.release()
        self.memory_usage -= size_mb * 1024 * 1024
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        return {
            'active_tasks': len(self.active_tasks),
            'available_file_slots': self.file_semaphore._value,
            'available_memory_slots': self.memory_semaphore._value,
            'memory_usage_mb': self.memory_usage // (1024 * 1024),
            'system_memory_percent': psutil.virtual_memory().percent,
            'cpu_percent': psutil.cpu_percent()
        }


class StreamingFileReader:
    """High-performance streaming file reader with async support."""
    
    def __init__(self, chunk_size: int = 64 * 1024, use_mmap: bool = True):
        self.chunk_size = chunk_size
        self.use_mmap = use_mmap
        self.logger = logging.getLogger(__name__)
    
    async def read_file_chunks(self, file_path: Union[str, Path], 
                              encoding: str = 'utf-8') -> AsyncGenerator[bytes, None]:
        """Stream file content in chunks."""
        file_path = Path(file_path)
        
        try:
            file_size = await aiofiles.os.stat(file_path)
            file_size = file_size.st_size
            
            # Use memory mapping for large files
            if self.use_mmap and file_size > self.chunk_size * 10:
                async for chunk in self._read_with_mmap(file_path):
                    yield chunk
            else:
                async for chunk in self._read_with_aiofiles(file_path):
                    yield chunk
                    
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    async def _read_with_mmap(self, file_path: Path) -> AsyncGenerator[bytes, None]:
        """Read file using memory mapping."""
        try:
            # Run mmap operations in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _mmap_reader():
                with open(file_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        chunks = []
                        for i in range(0, len(mm), self.chunk_size):
                            chunks.append(mm[i:i + self.chunk_size])
                        return chunks
            
            chunks = await loop.run_in_executor(None, _mmap_reader)
            
            for chunk in chunks:
                yield chunk
                await asyncio.sleep(0)  # Yield control
                
        except Exception as e:
            self.logger.error(f"Error in mmap reading {file_path}: {e}")
            # Fallback to regular reading
            async for chunk in self._read_with_aiofiles(file_path):
                yield chunk
    
    async def _read_with_aiofiles(self, file_path: Path) -> AsyncGenerator[bytes, None]:
        """Read file using aiofiles."""
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk
                await asyncio.sleep(0)  # Yield control
    
    async def read_text_file_lines(self, file_path: Union[str, Path], 
                                  encoding: str = 'utf-8') -> AsyncGenerator[str, None]:
        """Stream text file content line by line."""
        try:
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                async for line in f:
                    yield line.rstrip('\n\r')
                    await asyncio.sleep(0)  # Yield control
        except UnicodeDecodeError as e:
            self.logger.warning(f"Unicode error in {file_path}: {e}")
            # Try with error handling
            async with aiofiles.open(file_path, 'r', encoding=encoding, errors='replace') as f:
                async for line in f:
                    yield line.rstrip('\n\r')
                    await asyncio.sleep(0)


class StreamingFileWriter:
    """High-performance streaming file writer with async support."""
    
    def __init__(self, buffer_size: int = 64 * 1024):
        self.buffer_size = buffer_size
        self.logger = logging.getLogger(__name__)
    
    async def write_chunks(self, file_path: Union[str, Path], 
                          chunks: AsyncGenerator[bytes, None], 
                          mode: str = 'wb') -> Dict[str, Any]:
        """Write chunks to file asynchronously."""
        file_path = Path(file_path)
        bytes_written = 0
        chunks_written = 0
        start_time = time.perf_counter()
        
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, mode, buffering=self.buffer_size) as f:
                async for chunk in chunks:
                    await f.write(chunk)
                    bytes_written += len(chunk)
                    chunks_written += 1
                    
                    # Periodic yield for other tasks
                    if chunks_written % 100 == 0:
                        await asyncio.sleep(0)
            
            write_time = time.perf_counter() - start_time
            
            return {
                'success': True,
                'file_path': str(file_path),
                'bytes_written': bytes_written,
                'chunks_written': chunks_written,
                'write_time': write_time,
                'throughput_mbps': (bytes_written / (1024 * 1024)) / write_time if write_time > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error writing to {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path),
                'bytes_written': bytes_written
            }
    
    async def write_lines(self, file_path: Union[str, Path], 
                         lines: AsyncGenerator[str, None], 
                         encoding: str = 'utf-8') -> Dict[str, Any]:
        """Write lines to text file asynchronously."""
        file_path = Path(file_path)
        lines_written = 0
        start_time = time.perf_counter()
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding=encoding, 
                                   buffering=self.buffer_size) as f:
                async for line in lines:
                    await f.write(line + '\n')
                    lines_written += 1
                    
                    if lines_written % 1000 == 0:
                        await asyncio.sleep(0)
            
            write_time = time.perf_counter() - start_time
            
            return {
                'success': True,
                'file_path': str(file_path),
                'lines_written': lines_written,
                'write_time': write_time,
                'lines_per_second': lines_written / write_time if write_time > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error writing lines to {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path),
                'lines_written': lines_written
            }


class AsyncFileProcessor:
    """Main async file processor with concurrent pipeline."""
    
    def __init__(self, resource_manager: Optional[ResourceManager] = None,
                 chunk_size: int = 64 * 1024):
        self.resource_manager = resource_manager or ResourceManager()
        self.reader = StreamingFileReader(chunk_size)
        self.writer = StreamingFileWriter(chunk_size)
        self.logger = logging.getLogger(__name__)
        
        # Processing statistics
        self.stats = {
            'files_processed': 0,
            'bytes_processed': 0,
            'processing_time': 0,
            'errors': 0
        }
    
    async def process_file(self, file_path: Union[str, Path], 
                          processor_func: Callable[[AsyncGenerator[bytes, None]], AsyncGenerator[bytes, None]],
                          output_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Process a single file with streaming."""
        file_path = Path(file_path)
        output_path = Path(output_path) if output_path else file_path.with_suffix(file_path.suffix + '.processed')
        
        start_time = time.perf_counter()
        
        # Acquire resources
        await self.resource_manager.acquire_file_slot()
        
        try:
            # Estimate memory usage
            file_size = await aiofiles.os.stat(file_path)
            file_size_mb = max(1, file_size.st_size // (1024 * 1024))
            
            await self.resource_manager.acquire_memory(file_size_mb)
            
            try:
                # Create processing pipeline
                input_chunks = self.reader.read_file_chunks(file_path)
                processed_chunks = processor_func(input_chunks)
                
                # Write processed chunks
                result = await self.writer.write_chunks(output_path, processed_chunks)
                
                # Update statistics
                processing_time = time.perf_counter() - start_time
                self.stats['files_processed'] += 1
                self.stats['bytes_processed'] += result.get('bytes_written', 0)
                self.stats['processing_time'] += processing_time
                
                result.update({
                    'input_file': str(file_path),
                    'processing_time': processing_time,
                    'resource_stats': self.resource_manager.get_stats()
                })
                
                return result
                
            finally:
                self.resource_manager.release_memory(file_size_mb)
                
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            self.stats['errors'] += 1
            return {
                'success': False,
                'error': str(e),
                'input_file': str(file_path),
                'processing_time': time.perf_counter() - start_time
            }
        finally:
            self.resource_manager.release_file_slot()
    
    async def process_files_batch(self, file_paths: List[Union[str, Path]], 
                                 processor_func: Callable[[AsyncGenerator[bytes, None]], AsyncGenerator[bytes, None]],
                                 output_dir: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """Process multiple files concurrently."""
        output_dir = Path(output_dir) if output_dir else None
        
        async def process_single(file_path):
            if output_dir:
                output_path = output_dir / Path(file_path).name
            else:
                output_path = None
            return await self.process_file(file_path, processor_func, output_path)
        
        # Process files concurrently
        tasks = [process_single(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Exception processing {file_paths[i]}: {result}")
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'input_file': str(file_paths[i])
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def copy_file_async(self, src: Union[str, Path], 
                             dst: Union[str, Path]) -> Dict[str, Any]:
        """High-performance async file copy."""
        src_path = Path(src)
        dst_path = Path(dst)
        
        start_time = time.perf_counter()
        
        await self.resource_manager.acquire_file_slot()
        
        try:
            # Get file size for memory management
            file_stat = await aiofiles.os.stat(src_path)
            file_size = file_stat.st_size
            file_size_mb = max(1, file_size // (1024 * 1024))
            
            await self.resource_manager.acquire_memory(file_size_mb)
            
            try:
                # Ensure destination directory exists
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Stream copy
                input_chunks = self.reader.read_file_chunks(src_path)
                result = await self.writer.write_chunks(dst_path, input_chunks)
                
                copy_time = time.perf_counter() - start_time
                
                result.update({
                    'source_file': str(src_path),
                    'destination_file': str(dst_path),
                    'file_size': file_size,
                    'copy_time': copy_time,
                    'throughput_mbps': (file_size / (1024 * 1024)) / copy_time if copy_time > 0 else 0
                })
                
                return result
                
            finally:
                self.resource_manager.release_memory(file_size_mb)
                
        except Exception as e:
            self.logger.error(f"Error copying {src_path} to {dst_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'source_file': str(src_path),
                'destination_file': str(dst_path),
                'copy_time': time.perf_counter() - start_time
            }
        finally:
            self.resource_manager.release_file_slot()
    
    async def process_directory_tree(self, root_dir: Union[str, Path], 
                                   processor_func: Callable[[AsyncGenerator[bytes, None]], AsyncGenerator[bytes, None]],
                                   file_pattern: str = "*",
                                   output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Process all files in a directory tree."""
        root_path = Path(root_dir)
        output_path = Path(output_dir) if output_dir else root_path / "processed"
        
        start_time = time.perf_counter()
        
        # Find all matching files
        all_files = list(root_path.rglob(file_pattern))
        file_paths = [f for f in all_files if f.is_file()]
        
        self.logger.info(f"Found {len(file_paths)} files to process in {root_path}")
        
        # Process files in batches to manage memory
        batch_size = min(50, self.resource_manager.max_concurrent_files)
        results = []
        
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
            
            batch_results = await self.process_files_batch(batch, processor_func, output_path)
            results.extend(batch_results)
            
            # Brief pause between batches
            await asyncio.sleep(0.1)
        
        total_time = time.perf_counter() - start_time
        successful = sum(1 for r in results if r.get('success', False))
        
        return {
            'success': True,
            'root_directory': str(root_path),
            'output_directory': str(output_path),
            'total_files': len(file_paths),
            'successful_files': successful,
            'failed_files': len(file_paths) - successful,
            'total_time': total_time,
            'files_per_second': len(file_paths) / total_time if total_time > 0 else 0,
            'results': results,
            'final_stats': self.get_stats()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        stats.update(self.resource_manager.get_stats())
        
        if stats['processing_time'] > 0:
            stats['avg_throughput_mbps'] = (stats['bytes_processed'] / (1024 * 1024)) / stats['processing_time']
            stats['avg_files_per_second'] = stats['files_processed'] / stats['processing_time']
        else:
            stats['avg_throughput_mbps'] = 0
            stats['avg_files_per_second'] = 0
        
        return stats


# Example processor functions
async def identity_processor(chunks: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
    """Identity processor - passes chunks through unchanged."""
    async for chunk in chunks:
        yield chunk

async def uppercase_text_processor(chunks: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
    """Convert text to uppercase."""
    async for chunk in chunks:
        try:
            text = chunk.decode('utf-8')
            yield text.upper().encode('utf-8')
        except UnicodeDecodeError:
            # Pass binary data unchanged
            yield chunk

async def line_counter_processor(chunks: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
    """Add line numbers to text files."""
    line_number = 1
    buffer = b""
    
    async for chunk in chunks:
        buffer += chunk
        lines = buffer.split(b'\n')
        buffer = lines[-1]  # Keep incomplete line in buffer
        
        for line in lines[:-1]:
            numbered_line = f"{line_number:6d}: ".encode('utf-8') + line + b'\n'
            yield numbered_line
            line_number += 1
    
    # Handle remaining buffer
    if buffer:
        numbered_line = f"{line_number:6d}: ".encode('utf-8') + buffer
        yield numbered_line


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        # Initialize processor
        processor = AsyncFileProcessor()
        
        # Example: Process a single file
        # result = await processor.process_file(
        #     "example.txt", 
        #     uppercase_text_processor,
        #     "example_upper.txt"
        # )
        # print(f"Processing result: {result}")
        
        # Example: Copy file
        # copy_result = await processor.copy_file_async("source.txt", "destination.txt")
        # print(f"Copy result: {copy_result}")
        
        print("Async File Processor initialized successfully!")
        print(f"Resource limits: {processor.resource_manager.get_stats()}")
    
    # Run example
    # asyncio.run(main())
    print("Async File Processor module loaded successfully!")
