import os

def create_init_files():
    """Create __init__.py files in all Python packages"""
    packages = [
        'src',
        'src/indicators',
        'src/strategy', 
        'src/risk_management',
        'src/data_handler',
        'src/backtesting',
        'src/gui',
        'src/ml_models',
        'src/utils'
    ]
    
    for package in packages:
        init_file = os.path.join(package, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f'"""Package: {package}"""\n')
            print(f"Created: {init_file}")

if __name__ == "__main__":
    create_init_files()