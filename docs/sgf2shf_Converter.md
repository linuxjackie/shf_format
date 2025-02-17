# sgf2shf Converter

將SGF（Smart Game Format）格式的圍棋棋譜轉換為SHF（Si Huo Format）格式的死活題工具。

## 安裝

確保你的環境中已安裝Python 3.x，並且有以下依賴：

```bash
pip install sgf
```

## 使用方法

1. **克隆本倉庫**:
   ```bash
   git clone https://github.com/linuxjackie/shf_format
   cd sgf2shf
   ```

2. **運行轉換器**:

   - 直接從命令行運行腳本，提供SGF內容作為參數:
     ```bash
     python sgf2shf.py ";FF[4]GM[1]SZ[9]AB[aa][ca][ea][gc][ic]AW[bb][cb][eb][fb][gb]B[cc];W[bc];B[dc];W[ec]"
     ```

   - 或者，從文件中讀取SGF內容（假設文件名為`game.sgf`）:
     ```bash
     python sgf2shf.py -f game.sgf
     ```

   - 其他選項:
     ```bash
     python sgf2shf.py -h  # 查看幫助
     python sgf2shf.py -f game.sgf -o output.shf  # 指定輸出文件
     python sgf2shf.py -f game.sgf -v  # 啟用詳細輸出
     ```

## 代碼

以下是`sgf2shf.py`的內容：

```python
import re
from sgf import SGFParser
import argparse
import sys

def sgf_to_shf(sgf_content):
    """
    Convert SGF content to SHF format.

    :param sgf_content: SGF format content as a string
    :return: SHF formatted string
    """
    collection = SGFParser(sgf_content).parse()
    game = collection[0]
    
    size = game.get_size()
    shf_size = '1' if size == 9 else ('2' if size == 13 else '3')
    
    setup = []
    for node in game.nodes:
        if 'AB' in node:
            setup.extend([f'B{convert_coord(move)}' for move in node['AB']])
        if 'AW' in node:
            setup.extend([f'W{convert_coord(move)}' for move in node['AW']])
    
    solutions = []
    for variation in game.mainline():
        moves = []
        for node in variation:
            if 'B' in node:
                moves.append(f'B{convert_coord(node["B"])}')
            if 'W' in node:
                moves.append(f'W{convert_coord(node["W"])}')
        if moves:  
            solutions.append(','.join(moves))
    
    shf = f"00001:{shf_size}:{','.join(setup)}"
    for i, solution in enumerate(solutions, 1):
        if i == 1:
            shf += f":+{solution}"
        elif i == 2:
            shf += f":-{solution}"
        else:
            shf += f"/{solution}"
    shf += ","
    
    return shf

def convert_coord(sgf_coord):
    """
    Convert SGF coordinates to SHF coordinates.

    :param sgf_coord: SGF coordinate format like 'aa'
    :return: SHF coordinate format like 'aa'
    """
    col = ord(sgf_coord[0]) - ord('a')
    row = ord(sgf_coord[1]) - ord('a')
    return f"{chr(ord('a') + col)}{chr(ord('a') + row)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert SGF to SHF format.")
    parser.add_argument("-f", "--file", help="Input SGF file path")
    parser.add_argument("-o", "--output", default=None, help="Output SHF file name")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("sgf_content", nargs='?', help="SGF content as a string")
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as file:
            sgf_content = file.read()
    elif args.sgf_content:
        sgf_content = args.sgf_content
    else:
        sgf_content = sys.stdin.read()

    shf_result = sgf_to_shf(sgf_content)

    if args.output:
        with open(args.output, 'w') as file:
            file.write(shf_result)
        if args.verbose:
            print(f"SHF data has been written to {args.output}")
    else:
        print(shf_result)
```

## 注意

- 這個工具假設SGF文件的第一個變化是正確解答，第二個變化（如果存在）是錯誤解答，後續變化則視為變化或可選解答。
- `convert_coord`函數簡化了SGF的座標轉換到SHF的座標系統。
- ID固定為`00001`，實際使用中可能需要生成或指定唯一的ID。

## 貢獻

歡迎任何形式的貢獻，包括但不限於錯誤修復、功能增強、文檔改進等。請先開一個議題討論你的改動。
