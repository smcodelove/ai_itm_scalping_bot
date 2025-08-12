"""
Test script to verify the development environment setup
Run this to ensure all components are working correctly
"""

import os
import sys
import json
from datetime import datetime

def test_environment():
    """Test the development environment setup"""
    print("🚀 Testing AI ITM Scalping Bot Environment Setup")
    print("=" * 50)
    
    # Test 1: Python version
    print(f"✅ Python Version: {sys.version}")
    
    # Test 2: Project structure
    required_dirs = [
        'src', 'data', 'config', 'tests', 'logs', 
        'src/indicators', 'src/strategy', 'src/risk_management',
        'src/data_handler', 'src/gui', 'src/utils'
    ]
    
    print("\n📁 Project Structure:")
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - Missing!")
    
    # Test 3: Required packages
    print("\n📦 Testing Package Imports:")
    packages_to_test = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('matplotlib.pyplot', 'plt'),
        ('sqlite3', 'sqlite3'),
        ('tkinter', 'tk'),
        ('json', 'json'),
        ('datetime', 'datetime')
    ]
    
    for package, alias in packages_to_test:
        try:
            exec(f"import {package} as {alias}")
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package} - {e}")
    
    # Test 4: Configuration files
    print("\n⚙️ Configuration Files:")
    config_files = ['config/settings.json']
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    json.load(f)
                print(f"✅ {config_file} - Valid JSON")
            except json.JSONDecodeError:
                print(f"❌ {config_file} - Invalid JSON")
        else:
            print(f"❌ {config_file} - Missing!")
    
    # Test 5: Logger
    print("\n📝 Testing Logger:")
    try:
        sys.path.append('src')
        from utils.logger import logger
        logger.info("Logger test successful!")
        print("✅ Logger working correctly")
    except Exception as e:
        print(f"❌ Logger error: {e}")
    
    # Test 6: Create sample data directory
    print("\n📊 Setting up sample data:")
    sample_dir = "data/sample"
    os.makedirs(sample_dir, exist_ok=True)
    print(f"✅ Sample data directory: {sample_dir}")
    
    print("\n🎉 Environment setup test completed!")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_environment()