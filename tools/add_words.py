import os
import re

FILE_PATH = 'words.txt'

def main():
    if not os.path.exists(FILE_PATH):
        open(FILE_PATH, 'w', encoding='utf-8').close()

    # 1. Load memory
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        existing_words = {line.strip().upper() for line in f if line.strip()}

    print(f"Loaded {len(existing_words)} words into memory.")
    print("Type '!QUIT' to exit and sort.")
    print("Input method: Single words, line-by-line pasting, or comma/space separated lists.\n")

    new_additions = 0

    # 2. Append mode with batch-parsing logic
    with open(FILE_PATH, 'a', encoding='utf-8') as f:
        while True:
            try:
                raw_input = input("Enter word(s): ").strip().upper()
            except (KeyboardInterrupt, EOFError):
                print("\nForced interrupt detected. Halting input.")
                break

            if not raw_input:
                continue
            
            if raw_input == '!QUIT':
                break

            # Logic testing: Split input by any whitespace or commas 
            # This turns "ALPHA, BETA GAMMA" into ['ALPHA', 'BETA', 'GAMMA']
            words_to_process = [w for w in re.split(r'[\s,]+', raw_input) if w]

            for word in words_to_process:
                # Catch stray quit commands hidden in a pasted block
                if word == '!QUIT':
                    print("\nQuit command detected in batch block. Halting.")
                    break 

                if word in existing_words:
                    print(f"  [X] Rejected: '{word}' already exists.")
                else:
                    existing_words.add(word)
                    f.write(f"{word}\n")
                    new_additions += 1
                    print(f"  [+] Accepted: '{word}'.")
            
            # Flush to disk only once per input event, even if 100 words were parsed
            if words_to_process:
                f.flush() 

            if '!QUIT' in words_to_process:
                break

    # 3. Post-processing sort
    if new_additions > 0:
        print("\nRe-sorting entire dictionary...")
        sorted_words = sorted(existing_words)
        
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sorted_words) + '\n')
            
        print(f"Process complete. {new_additions} words added and file sorted.")
    else:
        print("\nNo modifications made. Exiting.")

if __name__ == '__main__':
    main()