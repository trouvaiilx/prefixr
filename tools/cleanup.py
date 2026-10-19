import os
import re
import time

FILE_PATH = 'words.txt'
CLEAN_FILE_PATH = 'words_clean.txt'

def sanitize_wordlist():
    if not os.path.exists(FILE_PATH):
        print(f"[!] Error: '{FILE_PATH}' not found in the current directory.")
        return

    print("Starting regex sanitization and deduplication...")
    start_time = time.time()
    
    unique_words = set()
    raw_line_count = 0
    completely_discarded = 0

    # Compile regex for C-level execution speed.
    # [^A-Z] means: Match anything that is NOT an uppercase A-Z character.
    pattern = re.compile(r'[^A-Z]')

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            raw_line_count += 1
            
            # 1. Force uppercase
            raw_word = line.strip().upper()
            
            # 2. Sanitize: Sub out all special characters, numbers, and whitespaces
            # Example: "PEXELIZUMAB|||" becomes "PEXELIZUMAB"
            clean_word = pattern.sub('', raw_word)
            
            # 3. Insert to Set (Handles deduplication automatically)
            if clean_word:
                unique_words.add(clean_word)
            else:
                # Tracks lines that were purely garbage (e.g., a line that was just "---")
                completely_discarded += 1

    final_count = len(unique_words)
    duplicates_and_junk_removed = raw_line_count - final_count

    print(f"\nSorting {final_count} perfectly clean words...")
    sorted_words = sorted(unique_words)

    # Write to a safe backup file to prevent catastrophic data loss
    print(f"Writing output to '{CLEAN_FILE_PATH}'...")
    with open(CLEAN_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_words) + '\n')

    elapsed = time.time() - start_time

    # Data Analytics
    print("\n" + "="*30)
    print("      SANITIZATION REPORT      ")
    print("="*30)
    print(f"Total lines read:      {raw_line_count:,}")
    print(f"Pure garbage dropped:  {completely_discarded:,}")
    print(f"Duplicates eliminated: {duplicates_and_junk_removed:,}")
    print(f"Final dictionary size: {final_count:,}")
    print(f"Execution time:        {elapsed:.3f} seconds")
    print("="*30)

if __name__ == '__main__':
    sanitize_wordlist()