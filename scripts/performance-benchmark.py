#!/usr/bin/env python3
"""
Performance Benchmarking Tool for WhyML Advanced Scraping
Measures performance metrics and generates comprehensive reports
"""

import time
import asyncio
import statistics
import json
import yaml
import sys
import os
from datetime import datetime
from pathlib import Path
import subprocess
import psutil
import argparse

# Add WhyML to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from whyml.scrapers.url_scraper import URLScraper
    from whyml.processor import WhyMLProcessor
except ImportError as e:
    print(f"Warning: Could not import WhyML modules: {e}")
    print("Running in CLI-only mode")

class PerformanceBenchmark:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'benchmarks': {}
        }
        
    def _get_system_info(self):
        """Get system information for benchmark context"""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'python_version': sys.version,
            'platform': sys.platform
        }
    
    def _measure_cli_command(self, command, iterations=3):
        """Measure CLI command performance"""
        times = []
        memory_usage = []
        
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...")
            
            # Measure memory before
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss
            
            # Measure execution time
            start_time = time.time()
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                end_time = time.time()
                
                if result.returncode != 0:
                    print(f"    Warning: Command failed with code {result.returncode}")
                    print(f"    Error: {result.stderr}")
                    continue
                    
            except subprocess.TimeoutExpired:
                print(f"    Warning: Command timed out")
                continue
                
            # Measure memory after
            memory_after = process.memory_info().rss
            
            execution_time = end_time - start_time
            memory_used = memory_after - memory_before
            
            times.append(execution_time)
            memory_usage.append(memory_used)
            
            print(f"    Time: {execution_time:.2f}s, Memory: {memory_used/1024/1024:.1f}MB")
        
        if not times:
            return None
            
        return {
            'execution_time': {
                'mean': statistics.mean(times),
                'median': statistics.median(times),
                'min': min(times),
                'max': max(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0
            },
            'memory_usage': {
                'mean': statistics.mean(memory_usage),
                'median': statistics.median(memory_usage),
                'min': min(memory_usage),
                'max': max(memory_usage)
            },
            'iterations': len(times),
            'success_rate': len(times) / iterations
        }
    
    def benchmark_basic_scraping(self):
        """Benchmark basic website scraping"""
        print("\n🔍 Benchmarking Basic Scraping...")
        
        command = "whyml scrape https://example.com -o benchmark-basic.yaml"
        result = self._measure_cli_command(command)
        
        if result:
            self.results['benchmarks']['basic_scraping'] = result
            print(f"✅ Basic scraping: {result['execution_time']['mean']:.2f}s avg")
        else:
            print("❌ Basic scraping benchmark failed")
    
    def benchmark_structure_simplification(self):
        """Benchmark structure simplification features"""
        print("\n🏗️ Benchmarking Structure Simplification...")
        
        tests = [
            ("max_depth", "whyml scrape https://example.com --max-depth 2 -o benchmark-depth.yaml"),
            ("flatten_containers", "whyml scrape https://example.com --flatten-containers -o benchmark-flatten.yaml"),
            ("combined_simplification", "whyml scrape https://example.com --max-depth 3 --flatten-containers --simplify-structure -o benchmark-combined.yaml")
        ]
        
        for test_name, command in tests:
            print(f"  Testing {test_name}...")
            result = self._measure_cli_command(command)
            
            if result:
                self.results['benchmarks'][f'simplification_{test_name}'] = result
                print(f"  ✅ {test_name}: {result['execution_time']['mean']:.2f}s avg")
            else:
                print(f"  ❌ {test_name} benchmark failed")
    
    def benchmark_selective_sections(self):
        """Benchmark selective section generation"""
        print("\n📊 Benchmarking Selective Sections...")
        
        tests = [
            ("metadata_only", "whyml scrape https://example.com --section metadata -o benchmark-metadata.yaml"),
            ("analysis_only", "whyml scrape https://example.com --section analysis -o benchmark-analysis.yaml"),
            ("multi_sections", "whyml scrape https://example.com --section metadata --section analysis -o benchmark-multi.yaml")
        ]
        
        for test_name, command in tests:
            print(f"  Testing {test_name}...")
            result = self._measure_cli_command(command)
            
            if result:
                self.results['benchmarks'][f'selective_{test_name}'] = result
                print(f"  ✅ {test_name}: {result['execution_time']['mean']:.2f}s avg")
            else:
                print(f"  ❌ {test_name} benchmark failed")
    
    def benchmark_testing_workflow(self):
        """Benchmark testing and comparison workflow"""
        print("\n🧪 Benchmarking Testing Workflow...")
        
        command = "whyml scrape https://example.com --test-conversion --output-html benchmark-test.html -o benchmark-workflow.yaml"
        result = self._measure_cli_command(command, iterations=2)  # Fewer iterations for complex test
        
        if result:
            self.results['benchmarks']['testing_workflow'] = result
            print(f"✅ Testing workflow: {result['execution_time']['mean']:.2f}s avg")
        else:
            print("❌ Testing workflow benchmark failed")
    
    def benchmark_file_sizes(self):
        """Benchmark output file sizes"""
        print("\n📁 Analyzing Output File Sizes...")
        
        file_sizes = {}
        benchmark_files = [
            ('basic', 'benchmark-basic.yaml'),
            ('depth_limited', 'benchmark-depth.yaml'),
            ('flattened', 'benchmark-flatten.yaml'),
            ('combined', 'benchmark-combined.yaml'),
            ('metadata_only', 'benchmark-metadata.yaml'),
            ('analysis_only', 'benchmark-analysis.yaml')
        ]
        
        for name, filename in benchmark_files:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                file_sizes[name] = size
                print(f"  {name}: {size} bytes ({size/1024:.1f} KB)")
        
        if file_sizes:
            self.results['benchmarks']['file_sizes'] = file_sizes
            
            # Calculate optimization ratios
            if 'basic' in file_sizes:
                basic_size = file_sizes['basic']
                optimizations = {}
                
                for name, size in file_sizes.items():
                    if name != 'basic':
                        ratio = (basic_size - size) / basic_size * 100
                        optimizations[name] = ratio
                        print(f"  {name} optimization: {ratio:.1f}% reduction")
                
                self.results['benchmarks']['size_optimizations'] = optimizations
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📋 Generating Performance Report...")
        
        # Calculate overall performance metrics
        if self.results['benchmarks']:
            execution_times = []
            for benchmark_name, data in self.results['benchmarks'].items():
                if isinstance(data, dict) and 'execution_time' in data:
                    execution_times.append(data['execution_time']['mean'])
            
            if execution_times:
                self.results['summary'] = {
                    'total_benchmarks': len(execution_times),
                    'average_execution_time': statistics.mean(execution_times),
                    'fastest_benchmark': min(execution_times),
                    'slowest_benchmark': max(execution_times),
                    'performance_rating': self._calculate_performance_rating(execution_times)
                }
        
        # Save detailed results
        with open('performance-benchmark-results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✅ Detailed results saved to performance-benchmark-results.json")
        
        # Generate summary report
        self._print_summary_report()
    
    def _calculate_performance_rating(self, times):
        """Calculate overall performance rating"""
        avg_time = statistics.mean(times)
        
        if avg_time < 5:
            return "Excellent"
        elif avg_time < 10:
            return "Good"
        elif avg_time < 20:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _print_summary_report(self):
        """Print summary performance report"""
        print("\n" + "="*50)
        print("🏆 PERFORMANCE BENCHMARK SUMMARY")
        print("="*50)
        
        if 'summary' in self.results:
            summary = self.results['summary']
            print(f"📊 Total Benchmarks: {summary['total_benchmarks']}")
            print(f"⏱️  Average Time: {summary['average_execution_time']:.2f}s")
            print(f"🚀 Fastest: {summary['fastest_benchmark']:.2f}s")
            print(f"🐌 Slowest: {summary['slowest_benchmark']:.2f}s")
            print(f"🎯 Rating: {summary['performance_rating']}")
        
        # File size optimizations
        if 'size_optimizations' in self.results['benchmarks']:
            print(f"\n💾 File Size Optimizations:")
            for name, ratio in self.results['benchmarks']['size_optimizations'].items():
                print(f"   {name}: {ratio:.1f}% reduction")
        
        # Performance recommendations
        print(f"\n💡 Recommendations:")
        if 'summary' in self.results:
            avg_time = self.results['summary']['average_execution_time']
            if avg_time > 15:
                print("   - Consider using selective sections for faster processing")
                print("   - Use structure simplification for complex sites")
            if avg_time < 5:
                print("   - Excellent performance! Ready for production workloads")
        
        print(f"\n🎉 Benchmark Complete!")
        print(f"Timestamp: {self.results['timestamp']}")
    
    def cleanup_benchmark_files(self):
        """Clean up benchmark output files"""
        print("\n🧹 Cleaning up benchmark files...")
        
        benchmark_files = [
            'benchmark-basic.yaml',
            'benchmark-depth.yaml', 
            'benchmark-flatten.yaml',
            'benchmark-combined.yaml',
            'benchmark-metadata.yaml',
            'benchmark-analysis.yaml',
            'benchmark-multi.yaml',
            'benchmark-workflow.yaml',
            'benchmark-test.html'
        ]
        
        for filename in benchmark_files:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"  Removed {filename}")
    
    def run_full_benchmark(self):
        """Run complete performance benchmark suite"""
        print("🚀 Starting WhyML Performance Benchmark Suite")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            self.benchmark_basic_scraping()
            self.benchmark_structure_simplification()
            self.benchmark_selective_sections()
            self.benchmark_testing_workflow()
            self.benchmark_file_sizes()
            self.generate_performance_report()
            
        except KeyboardInterrupt:
            print("\n⚠️ Benchmark interrupted by user")
        except Exception as e:
            print(f"\n❌ Benchmark failed: {e}")
        finally:
            end_time = time.time()
            total_time = end_time - start_time
            print(f"\n⏱️ Total benchmark time: {total_time:.2f} seconds")
            
            # Optional cleanup
            cleanup_choice = input("\n🧹 Clean up benchmark files? (y/N): ").lower()
            if cleanup_choice == 'y':
                self.cleanup_benchmark_files()

def main():
    parser = argparse.ArgumentParser(description='WhyML Performance Benchmark Tool')
    parser.add_argument('--no-cleanup', action='store_true', help='Keep benchmark files after completion')
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations per test')
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    
    # Check if WhyML is available
    try:
        result = subprocess.run(['whyml', '--version'], capture_output=True)
        if result.returncode != 0:
            print("❌ WhyML CLI not available. Please install WhyML first.")
            sys.exit(1)
    except FileNotFoundError:
        print("❌ WhyML CLI not found. Please install WhyML and ensure it's in your PATH.")
        sys.exit(1)
    
    benchmark.run_full_benchmark()

if __name__ == "__main__":
    main()
