"""Basic smoke tests for web server"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    try:
        from web_server import app
        from web_server.api import auth, connections, ssh_terminal, agent_api
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test that Flask app can be created"""
    print("Testing Flask app creation...")
    try:
        from web_server.app import app, socketio
        assert app is not None
        assert socketio is not None
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Test that routes are registered"""
    print("Testing route registration...")
    try:
        from web_server.app import app
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'ok'
            print("✓ Routes registered successfully")
            return True
    except Exception as e:
        print(f"✗ Route test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("SSH & RDP Web Manager - Smoke Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_imports,
        test_app_creation,
        test_routes
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print()
        if test():
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
