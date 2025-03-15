import subprocess
import sys

def main():
    """Install required packages and language models"""
    print("Installing spaCy English language model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("Successfully installed spaCy English language model")
    except subprocess.CalledProcessError as e:
        print(f"Error installing spaCy language model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 