"""
ISRE (Intentional Semantic Reasoning Engine) Verification Test
============================================================
Run this: python verify_isre.py
"""

import subprocess
import sys
import os
from pathlib import Path

def find_isre():
    """Find ISRE project directory"""
    current = Path.cwd()
    
    # 1. Check if we are in the root (contains isre/ and tests/ or setup.py)
    if (current / 'isre').exists() and (current / 'isre').is_dir():
        return current
        
    names = [
        'isre', 'ISRE', 
        'Intentional Semantic Reasoning Engine', 
        'intentional-semantic-reasoning', 
        'semantic-reasoning'
    ]
    
    # 2. Check subdirectories or sibling directories
    for name in names:
        for base in [current, current.parent]:
            path = base / name
            if path.exists() and path.is_dir():
                # If this looks like the package dir (has __init__.py), return parent
                if (path / '__init__.py').exists():
                    return path.parent
                return path
    
    return None

def count_tests(project_dir):
    """Count test files"""
    tests_dir = project_dir / 'tests'
    if not tests_dir.exists():
        return 0, []
    
    test_files = list(tests_dir.glob('test_*.py')) + list(tests_dir.glob('*_test.py'))
    return len(test_files), test_files

def run_tests(project_dir):
    """Run pytest"""
    os.chdir(project_dir)
    
    for cmd in [
        ['pytest', 'tests/', '-v'],
        ['python', '-m', 'pytest', 'tests/', '-v'],
        ['pytest', '-v']
    ]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return -1, "TIMEOUT after 60s", ""
    
    return -1, "", "pytest not available"

def test_import(project_dir):
    """Try importing ISRE"""
    sys.path.insert(0, str(project_dir))
    
    try:
        import isre
        return True, f"✅ Module imported: {isre}"
    except ImportError as e:
        return False, f"❌ Import failed: {e}"

def test_basic_functionality(project_dir):
    """Try running a basic ISRE operation"""
    sys.path.insert(0, str(project_dir))
    
    try:
        # UPDATED: Use ISREPipeline instead of ISREOrchestrator
        try:
            from isre.pipeline.orchestrator import ISREPipeline as Orchestrator
            name = "ISREPipeline"
        except ImportError:
            from isre.pipeline.orchestrator import ISREOrchestrator as Orchestrator
            name = "ISREOrchestrator"
        
        # Try to create orchestrator
        orchestrator = Orchestrator()
        
        # Try a simple processing
        result = orchestrator.process("Hello world")
        
        return True, f"✅ Processed test input successfully using {name}"
    except Exception as e:
        return False, f"❌ Processing failed: {e}"

def main():
    print("=" * 70)
    print("ISRE VERIFICATION TEST")
    print("=" * 70)
    
    # Find project
    print("\n[1/5] Finding ISRE project...")
    project_dir = find_isre()
    
    if not project_dir:
        print("❌ ISRE project not found")
        print("Current dir:", Path.cwd())
        return
    
    print(f"✅ Found: {project_dir}")
    
    # Count tests
    print("\n[2/5] Counting test files...")
    test_count, test_files = count_tests(project_dir)
    
    if test_count == 0:
        print("❌ No test files found")
    else:
        print(f"✅ Found {test_count} test files")
        for f in test_files[:3]:
            print(f"   - {f.name}")
    
    # Run tests
    print("\n[3/5] Running pytest...")
    print("-" * 70)
    
    if test_count > 0:
        returncode, stdout, stderr = run_tests(project_dir)
        print(stdout)
        if stderr and "warning" not in stderr.lower():
            print("ERRORS:", stderr)
        print("-" * 70)
        
        if returncode == 0:
            print("✅ ALL TESTS PASSED")
            test_result = "PASS"
        else:
            print(f"❌ Tests failed (exit code: {returncode})")
            test_result = "FAIL"
    else:
        print("⏭️  Skipping (no tests found)")
        test_result = "SKIP"
        returncode = -1
    
    # Test import
    print("\n[4/5] Testing module import...")
    import_ok, import_msg = test_import(project_dir)
    print(import_msg)
    
    # Test functionality
    print("\n[5/5] Testing basic functionality...")
    func_ok, func_msg = test_basic_functionality(project_dir)
    print(func_msg)
    
    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Project: {project_dir.name}")
    print(f"Test files: {test_count}")
    print(f"Pytest: {test_result}")
    print(f"Import: {'PASS' if import_ok else 'FAIL'}")
    print(f"Functionality: {'PASS' if func_ok else 'FAIL'}")
    print("=" * 70)
    
    # Overall verdict
    if returncode == 0 and import_ok and func_ok:
        print("\n🎉 VERDICT: ISRE IS WORKING")
    elif test_count == 0:
        print("\n⚠️  VERDICT: NO TESTS FOUND - CANNOT VERIFY")
    else:
        print("\n❌ VERDICT: ISRE HAS ISSUES")

if __name__ == "__main__":
    main()