#!/usr/bin/env python3
"""
Verification script for the UUID schema fix.
Run this to verify that the new workflow resolves the FK mismatch issue.

Usage: python test_uuid_fix.py
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def check_model_consistency():
    """Verify that all models use UUID consistently"""
    print("🔍 Checking model schema consistency...")
    
    from app.db.models import Location, Post, PostMedia, PostLike, PostComment
    
    models_to_check = [
        ("Location.id", Location.id.type),
        ("Post.id", Post.id.type),
        ("Post.location_id", Post.location_id.type),
        ("PostMedia.id", PostMedia.id.type),
        ("PostMedia.post_id", PostMedia.post_id.type),
        ("PostLike.post_id", PostLike.post_id.type),
        ("PostComment.post_id", PostComment.post_id.type),
    ]
    
    for field_name, field_type in models_to_check:
        type_str = str(field_type)
        if "UUID" in type_str:
            print(f"✅ {field_name}: {type_str}")
        else:
            print(f"❌ {field_name}: {type_str} (should be UUID)")
            return False
    
    return True

def check_seed_script():
    """Verify that the seed script uses correct imports"""
    print("\n🔍 Checking seed script...")
    
    try:
        from seed_db import seed_phase1
        import inspect
        
        # Check that it's async
        if not inspect.iscoroutinefunction(seed_phase1):
            print("❌ seed_phase1 should be an async function")
            return False
        
        # Check imports in the source
        source = inspect.getsource(seed_phase1.__module__)
        
        required_imports = [
            "from app.db.models import Base, Location, Post, PostMedia",
            "from app.db.session import AsyncSessionLocal, async_engine"
        ]
        
        forbidden_imports = [
            "from src.models",
            "db.drop_all()",
            "db.create_all()"
        ]
        
        for required in required_imports:
            if required not in source:
                print(f"❌ Missing required import: {required}")
                return False
            print(f"✅ Found required import: {required}")
        
        for forbidden in forbidden_imports:
            if forbidden in source:
                print(f"❌ Found forbidden pattern: {forbidden}")
                return False
        
        print("✅ Seed script uses correct FastAPI models and async session")
        return True
        
    except Exception as e:
        print(f"❌ Error checking seed script: {e}")
        return False

def check_flask_vs_fastapi():
    """Show the difference between Flask and FastAPI models"""
    print("\n🔍 Demonstrating Flask vs FastAPI model difference...")
    
    try:
        from src.models.post import Post as FlaskPost
        from app.db.models import Post as FastAPIPost
        
        flask_type = str(FlaskPost.id.type)
        fastapi_type = str(FastAPIPost.id.type)
        
        print(f"Flask Post.id type: {flask_type}")
        print(f"FastAPI Post.id type: {fastapi_type}")
        
        if "INTEGER" in flask_type.upper() and "UUID" in fastapi_type:
            print("✅ Confirmed: This is exactly the mismatch we fixed!")
            return True
        else:
            print("❌ Unexpected types found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Flask vs FastAPI: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🧪 UUID Schema Fix Verification")
    print("=" * 40)
    
    checks = [
        ("Model Consistency", check_model_consistency),
        ("Seed Script", check_seed_script),
        ("Flask vs FastAPI", check_flask_vs_fastapi),
    ]
    
    passed = 0
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            print()
    
    print(f"📊 Results: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("\n🎉 All checks passed!")
        print("\n📋 Recommended workflow for PostgreSQL:")
        print("1. alembic upgrade head    # Create UUID schema")
        print("2. python seed_db.py       # Seed with UUID data")
        print("3. python run_fastapi.py   # Run without FK errors")
        print("\n✅ This should resolve the schema mismatch issue!")
    else:
        print(f"\n❌ {len(checks) - passed} checks failed. Please review the implementation.")
    
    return passed == len(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)