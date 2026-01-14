import subprocess

def get_current_commit_hash():
    """Gets the current commit hash"""
    try:
        # Run git rev-parse HEAD
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit hash: {e}")
        return None
    except FileNotFoundError:
        print("Git not found on the system")
        return None
