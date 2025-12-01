import streamlit_authenticator as stauth
import sys

# --- GENERATE HASHED PASSWORDS ---

# IMPORTANT: This script requires streamlit-authenticator version 0.3.0 or newer.
# Please ensure you have the correct version by running:
# pip install --upgrade streamlit-authenticator

try:
    # Passwords to hash correspond to the example users in config.yaml
    passwords_to_hash = ["user123", "password456"] 
    
    # The Hasher expects a list of passwords
    hashed_gen = stauth.Hasher()

    print("---")
    print("Hashed Passwords Generated Successfully!")
    print("Copy the hashed passwords below and paste them into your config.yaml file.")
    print()
    print("For user 'jsmith':")
    print(f"  password: '{hashed_gen.hash(passwords_to_hash[0])}'")
    print()
    print("For user 'rdoe':")
    print(f"  password: '{hashed_gen.hash(passwords_to_hash[1])}'")
    print("---")

except Exception as e:
    print(f"\nAn error occurred: {e}", file=sys.stderr)
    print("This script is designed for streamlit-authenticator v0.3.0 and newer.", file=sys.stderr)
    print("Please upgrade your library by running the following command in your terminal:", file=sys.stderr)
    print("pip install --upgrade streamlit-authenticator", file=sys.stderr)
    sys.exit(1)
