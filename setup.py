"""
Setup script for Crypto Trading Bot

To install dependencies:
    pip install -r requirements.txt

To run the bot:
    python main.py
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def setup_environment():
    """Setup environment files"""
    print("Setting up environment...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Please:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Binance API credentials")
        print("3. Configure your trading parameters")
        return False
    
    # Check if directories exist
    directories = ['data', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/ directory")
    
    return True

def validate_config():
    """Validate configuration"""
    print("Validating configuration...")
    
    try:
        from config.config import Config
        Config.validate_config()
        print("✅ Configuration is valid!")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease check your .env file and ensure:")
        print("- BINANCE_API_KEY is set")
        print("- BINANCE_SECRET_KEY is set")
        print("- Other parameters are configured correctly")
        return False

def main():
    """Main setup function"""
    print("="*50)
    print("🤖 Crypto Trading Bot Setup")
    print("="*50)
    
    # Step 1: Install requirements
    if not install_requirements():
        return
    
    # Step 2: Setup environment
    if not setup_environment():
        return
    
    # Step 3: Validate configuration (skip if .env is empty)
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read().strip()
            if 'your_binance_api_key_here' not in content and content:
                validate_config()
    
    print("\n" + "="*50)
    print("🎉 Setup completed!")
    print("="*50)
    print("\nNext steps:")
    print("1. Configure your .env file with API credentials")
    print("2. Test connection: python main.py (choose option 1 for demo)")
    print("3. Run backtest: python main.py (choose option 3)")
    print("4. Start live trading: python main.py (choose option 2)")
    print("\n⚠️  Always test with demo mode first!")

if __name__ == "__main__":
    main()