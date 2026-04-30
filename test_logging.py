#!/usr/bin/env python3
"""Test debug logging"""
import sys
sys.path.insert(0, '/home/arunkumar/Documents/CODE/enterprise-rag-databricks/app')

from rag_utils import debug_log, error_log, chunk_text

print("\n=== Testing Debug Logging ===\n", file=sys.stderr)

debug_log('This is a debug message')
error_log('This is an error message')

test_text = 'Leave policy: 20 days annual. ' * 50
chunks = chunk_text(test_text)
debug_log(f'Created {len(chunks)} chunks')

print("\n=== Test Complete ===\n", file=sys.stderr)
