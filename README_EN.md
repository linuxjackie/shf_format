# SHF Format Specification (Smart Go Format)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

English | [繁體中文](README.md)

SHF is a file format designed for storing and exchanging Go (Weiqi/Baduk) life and death problems.

## Related Tools

All tools are located in the [shf_tools](shf_tools/) directory:

### [sgf2shf](shf_tools/sgf2shf/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SGF to SHF converter
- Supports batch conversion
- Automatic level extraction

### [shf2sqlite](shf_tools/shf2sqlite/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SHF to SQLite database converter
- Efficient database storage
- Supports batch import

### [sqlite2shf](shf_tools/sqlite2shf/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SQLite database to SHF converter
- Selective export support
- Data integrity preservation

### [shf_viewer](shf_tools/shf_viewer/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SHF format problem viewer
- Interactive interface
- Answer validation support

## Format Definition

Each line in an SHF file represents one life and death problem, formatted as follows:

```level:id:size:initial_positions:answers
```

### Field Descriptions

1. `level`: Difficulty level
   - Dan ranks: 1d-9d
   - Kyu ranks: 1k-30k
   - Unspecified: 00

2. `id`: Problem number
   - 5-digit number, e.g., 00001

3. `size`: Board size
   - 1: 9x9 board
   - 2: 13x13 board
   - 3: 19x19 board

4. `initial_positions`: Initial board position
   - Format: `[B|W][a-s][a-s]`
   - Example: `Ba1,Wb2,Bc3`
   - Optional: Comment can be added at the end using #, e.g., `Ba1,Wb2#This is a comment`

5. `answers`: Answer sequences
   - Format: `[+|-|/][B|W][a-s][a-s](,...)#comment`
   - +: Correct answer
   - -: Wrong answer
   - /: Variation
   - Each answer can contain multiple moves, separated by commas
   - Optional: Comments can be added after each answer using #

### Examples

Basic example:
```
1d:00001:3:Ba1,Wb2,Bc3:+Ba4,Wb5#correct move,/Wa4#variation,/Bc5#variation
```

Complex example (multiple variations):
```
2d:00015:3:Ba1,Wb2,Bc3,Wd4#Black to live:+Ba4,Wb5,Bc6#correct sequence,+Ba5,Wb6,Bc7#another way to live,-Bd5#this fails,/Wa4,Bb5,Wc6#white's variation
```

More examples can be found in the [examples](examples/) directory.

## Format Validation

Here's a simple Python format validator:

```python
import re

def validate_shf(line):
    """Validate SHF format"""
    # Split into parts
    parts = line.strip().split(':')
    if len(parts) != 5:
        return False, "Format error: needs 5 parts"
        
    level, id_, size, initial, answers = parts
    
    # Validate level
    if not re.match(r'^([1-9]d|[1-3][0-9]?k|00)$', level):
        return False, "Invalid level format"
        
    # Validate ID
    if not re.match(r'^\d{5}$', id_):
        return False, "ID must be 5 digits"
        
    # Validate board size
    if size not in ['1', '2', '3']:
        return False, "Board size must be 1, 2, or 3"
        
    # Validate initial positions
    positions = initial.split('#')[0]
    for pos in positions.split(','):
        if pos and not re.match(r'^[BW][a-s][a-s]$', pos):
            return False, f"Invalid position format: {pos}"
            
    # Validate answers
    for ans in answers.split(','):
        if not ans:
            continue
        if '#' in ans:
            ans = ans.split('#')[0]
        if not re.match(r'^[+\-/][BW][a-s][a-s]', ans):
            return False, f"Invalid answer format: {ans}"
            
    return True, "Format is valid"

# Usage example
line = "1d:00001:3:Ba1,Wb2,Bc3:+Ba4,Wb5#correct move,/Wa4#variation"
is_valid, message = validate_shf(line)
print(message)
```

## File Naming Convention

Recommended file naming format: `[level][id].shf`
Examples:
- `1d00001.shf`
- `2k00015.shf`

## Technical Specifications

1. Encoding: UTF-8
2. Line endings: Unix style (LF)
3. Coordinate system:
   - a-s represents positions 1-19
   - 'i' is not used
   - Top-left corner is a1

## Use Cases

1. Life and death problem database
2. Go teaching software
3. Problem collection exchange
4. Mobile applications

## Important Notes

1. All coordinates should be lowercase
2. Answer sequences should end with a comma
3. Comments should not contain special delimiters (:, #)
4. Each file can contain multiple lines, one problem per line

## FAQ

**Q: Why use colon as the delimiter?**
A: Colons rarely appear in Go terminology, reducing the chance of confusion.

**Q: How to handle problems beyond 99999?**
A: Create new series using letter prefixes: a00001, b00001, etc.

**Q: Can HTML tags be used in comments?**
A: It's not recommended to use any markup in comments to maintain format simplicity.

**Q: How to handle multiple possibilities in variations?**
A: Use multiple answer sequences starting with "/" to represent different variations.

## Contributing

Improvements and bug reports are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.

## License

This format specification is released under the MIT License. Anyone is free to use, modify, and distribute it. 