#!/usr/bin/env python3
"""
AI ITM Scalping Bot - GUI Launcher
Quick start script to launch GUI with existing backend
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup the environment for GUI launch"""
    
    # Get project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir
    
    # Add to Python path
    sys.path.insert(0, str(project_root))
    
    print("🔧 Environment Setup:")
    print(f"   Project Root: {project_root}")
    print(f"   Python Path: Added {project_root}")
    
    return project_root

def check_dependencies():
    """Check if all required dependencies are available"""
    
    required_packages = [
        ('tkinter', 'GUI framework'),
        ('matplotlib', 'Chart plotting'),
        ('pandas', 'Data processing'),
        ('numpy', 'Numerical computing'),
        ('sqlite3', 'Database')
    ]
    
    missing_packages = []
    
    print("\n📦 Checking Dependencies:")
    
    for package, description in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'matplotlib':
                import matplotlib
            elif package == 'pandas':
                import pandas
            elif package == 'numpy':
                import numpy
            elif package == 'sqlite3':
                import sqlite3
                
            print(f"   ✅ {package:<12} - {description}")
            
        except ImportError:
            print(f"   ❌ {package:<12} - {description} (MISSING)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install matplotlib pandas numpy")
        return False
    
    return True

def check_backend_components():
    """Check if backend components are available"""
    
    backend_components = [
        ('src.data_handler.csv_handler', 'Data Handler'),
        ('src.strategy.signal_generator', 'Strategy Engine'),
        ('src.risk_management.risk_controls', 'Risk Manager'),
        ('src.data_handler.database', 'Database'),
        ('src.backtesting.backtest_engine', 'Backtesting')
    ]
    
    print("\n🔍 Checking Backend Components:")
    
    missing_components = []
    
    for module_path, description in backend_components:
        try:
            __import__(module_path)
            print(f"   ✅ {description:<15} - {module_path}")
        except ImportError as e:
            print(f"   ❌ {description:<15} - {module_path} (MISSING)")
            missing_components.append((module_path, str(e)))
    
    if missing_components:
        print(f"\n⚠️  Missing backend components:")
        for module, error in missing_components:
            print(f"     - {module}: {error}")
        return False
    
    return True

def create_gui_directory():
    """Create GUI directory if it doesn't exist"""
    
    gui_dir = Path("src/gui")
    gui_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = gui_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# GUI Components\n")
    
    print(f"\n📁 GUI Directory: {gui_dir} (Ready)")
    
    return gui_dir

def save_main_gui_file():
    """Save the main GUI file"""
    
    gui_dir = create_gui_directory()
    gui_file = gui_dir / "main_window.py"
    
    # Check if we need to create the file
    if not gui_file.exists():
        print("⚠️  GUI file not found. Please save the main GUI code to:")
        print(f"   {gui_file}")
        print("\n💡 You can copy the GUI implementation from the previous response")
        return None
    
    print(f"✅ GUI File: {gui_file} (Found)")
    return gui_file

def run_system_test():
    """Run quick system test"""
    
    print("\n🧪 Running System Test:")
    
    try:
        # Test data handler
        from src.data_handler.csv_handler import CSVDataHandler
        data_handler = CSVDataHandler()
        test_data = data_handler.generate_sample_data("NIFTY", days=1)
        print(f"   ✅ Data Handler: Generated {len(test_data)} bars")
        
        # Test strategy
        from src.strategy.signal_generator import ITMScalpingSignals
        strategy = ITMScalpingSignals()
        signals = strategy.generate_signals(test_data)
        print(f"   ✅ Strategy Engine: Generated {len(signals)} signals")
        
        # Test risk manager
        from src.risk_management.risk_controls import RiskManager
        risk_mgr = RiskManager()
        print("   ✅ Risk Manager: Initialized successfully")
        
        # Test database
        from src.data_handler.database import TradingDatabase
        db = TradingDatabase()
        print("   ✅ Database: Connection successful")
        
        print("\n🎉 All backend components working perfectly!")
        return True
        
    except Exception as e:
        print(f"   ❌ System test failed: {e}")
        return False

def launch_gui():
    """Launch the GUI application"""
    
    print("\n🚀 Launching GUI Application...")
    
    try:
        # Import and run GUI
        from src.gui.main_window import ITMScalpingGUI
        
        print("   📱 Creating GUI application...")
        app = ITMScalpingGUI()
        
        print("   🎯 Starting main loop...")
        print("   💡 GUI should open in a new window")
        print("\n" + "="*50)
        print("🎉 AI ITM SCALPING BOT - GUI READY!")
        print("="*50)
        
        app.run()
        
    except ImportError as e:
        print(f"   ❌ Failed to import GUI: {e}")
        print("\n💡 Solution:")
        print("   1. Make sure GUI file is saved as: src/gui/main_window.py")
        print("   2. Copy the GUI implementation code to that file")
        print("   3. Run this launcher again")
        
    except Exception as e:
        print(f"   ❌ GUI launch failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check all dependencies are installed")
        print("   2. Verify backend components are working")
        print("   3. Check GUI file exists and is correct")

def main():
    """Main launcher function"""
    
    print("🎯 AI ITM SCALPING BOT - GUI LAUNCHER")
    print("="*50)
    
    # Setup environment
    project_root = setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        input("\n❌ Please install missing dependencies and try again...")
        return
    
    # Check backend
    if not check_backend_components():
        input("\n❌ Backend components missing. Please check project structure...")
        return
    
    # Create GUI directory
    create_gui_directory()
    
    # Check GUI file
    gui_file = save_main_gui_file()
    if gui_file is None:
        input("\n❌ Please create GUI file and try again...")
        return
    
    # Run system test
    if not run_system_test():
        input("\n❌ System test failed. Please check backend components...")
        return
    
    # Launch GUI
    try:
        launch_gui()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    finally:
        print("\n📴 GUI Launcher finished")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()