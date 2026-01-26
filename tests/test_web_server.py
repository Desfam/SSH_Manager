#!/usr/bin/env python3
"""Basic integration test for SSH & RDP Web Manager"""
import sys
import time
import subprocess

def test_server_startup():
    print("Testing server startup...")
    proc = subprocess.Popen(
        [sys.executable, '../start_web_server.py'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(5)
    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print("Server failed to start")
        return False, None
    print("Server started successfully")
    return True, proc

def main():
    print("=" * 60)
    print("SSH & RDP Web Manager - Integration Tests")
    print("=" * 60)
    server_proc = None
    try:
        success, server_proc = test_server_startup()
        if not success:
            return 1
        print("All tests passed!")
        return 0
    finally:
        if server_proc:
            server_proc.terminate()
            server_proc.wait()

if __name__ == '__main__':
    sys.exit(main())
