import os
import time

MAIN_FILE = 'words.txt'
MERGE_FILE = 'new_words.txt'

def merge_dictionaries():
    print("Starting bulk merge operation...")
    start_time = time.time()
    
    # 1. Load primary dictionary into a hash set
    if os.path.exists(MAIN_FILE):
        with open(MAIN_FILE, 'r', encoding='utf-8') as f:
            master_set = {line.strip().upper() for line in f if line.strip()}
    else:
        master_set = set()
    
    initial_count = len(master_set)
    print(f"Loaded {initial_count} words from {MAIN_FILE}.")

    # 2. Load the secondary dictionary
    if not os.path.exists(MERGE_FILE):
        print(f"\n[!] Error: '{MERGE_FILE}' not found in the directory. Aborting.")
        return

    with open(MERGE_FILE, 'r', encoding='utf-8') as f:
        # Set comprehension strips whitespaces and ensures format consistency
        new_words_set = {line.strip().upper() for line in f if line.strip()}
        
    print(f"Loaded {len(new_words_set)} words from {MERGE_FILE}.")

    # 3. The Core Logic: Mathematical Set Union
    # This executes in O(N) time at the C-level, instantly deduplicating all overlapping words.
    master_set.update(new_words_set)
    
    final_count = len(master_set)
    added_count = final_count - initial_count

    if added_count == 0:
        print("\nNo new unique words found. The primary file already contains all data. Exiting.")
        return

    # 4. Sort and overwrite disk
    print(f"\nFound {added_count} new unique words. Sorting arrays...")
    
    # Python's Timsort handles O(N log N) sorting of near-million element arrays in milliseconds
    sorted_words = sorted(master_set)
    
    print("Writing to disk...")
    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_words) + '\n')
        
    elapsed = time.time() - start_time
    print(f"\n[+] Merge complete in {elapsed:.3f} seconds.")
    print(f"[+] Total dictionary size: {final_count} words.")

if __name__ == '__main__':
    merge_dictionaries()