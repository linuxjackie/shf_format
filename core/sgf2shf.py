import re
from sgf import SGFParser
import argparse
import sys
import random

def validate_comment(comment):
    """驗證注釋是否包含特殊字符"""
    special_chars = [':', ',', '#', '\n', '\r']
    for char in special_chars:
        if char in comment:
            raise ValueError(f"注釋中包含非法字符: {char}")
    return comment

def validate_coordinates(coord, board_size):
    """驗證座標是否有效"""
    valid_chars = {
        9: 'abcdefghi',
        13: 'abcdefghijklm',
        19: 'abcdefghijklmnopqrs'
    }[board_size]
    
    if len(coord) != 2:
        raise ValueError(f"無效的座標長度: {coord}")
    if not (coord[0] in valid_chars and coord[1] in valid_chars):
        raise ValueError(f"座標超出棋盤範圍: {coord}")
    return coord

def generate_id():
    """生成唯一的5位數字ID"""
    return f"{random.randint(0, 99999):05d}"

def sgf_to_shf(sgf_content, problem_id=None):
    """
    Convert SGF content to SHF format.

    :param sgf_content: SGF format content as a string
    :param problem_id: Optional problem ID (5-digit number)
    :return: SHF formatted string
    """
    collection = SGFParser(sgf_content).parse()
    game = collection[0]
    
    # 驗證並設置 ID
    if problem_id:
        if not (problem_id.isdigit() and len(problem_id) == 5):
            raise ValueError("ID 必須是5位數字")
        shf_id = problem_id
    else:
        shf_id = generate_id()
    
    # 驗證並設置棋盤大小
    size = game.get_size()
    if size not in [9, 13, 19]:
        raise ValueError(f"不支持的棋盤大小: {size}")
    shf_size = '1' if size == 9 else ('2' if size == 13 else '3')
    
    # 處理初始狀態
    setup = []
    for node in game.nodes:
        if 'AB' in node:
            for move in node['AB']:
                coord = validate_coordinates(move, size)
                setup.append(f'B{convert_coord(coord)}')
        if 'AW' in node:
            for move in node['AW']:
                coord = validate_coordinates(move, size)
                setup.append(f'W{convert_coord(coord)}')
    
    # 處理初始注釋
    initial_comment = ""
    if 'C' in game.root:
        initial_comment = f"#{validate_comment(game.root['C'])}"
    
    # 處理答案序列
    solutions = []
    has_correct_answer = False
    for variation in game.variations():
        moves = []
        comment = ""
        last_color = None
        positions = set()
        
        for node in variation:
            if len(moves) >= 30:
                raise ValueError("移動序列超過30步限制")
                
            if 'B' in node:
                if last_color == 'B':
                    raise ValueError("連續黑棋落子")
                coord = validate_coordinates(node['B'], size)
                pos = convert_coord(coord)
                if pos in positions:
                    raise ValueError(f"重複落子: {pos}")
                moves.append(f'B{pos}')
                positions.add(pos)
                last_color = 'B'
            if 'W' in node:
                if last_color == 'W':
                    raise ValueError("連續白棋落子")
                coord = validate_coordinates(node['W'], size)
                pos = convert_coord(coord)
                if pos in positions:
                    raise ValueError(f"重複落子: {pos}")
                moves.append(f'W{pos}')
                positions.add(pos)
                last_color = 'W'
            if 'C' in node:
                comment = f"#{validate_comment(node['C'])}"
        
        if moves:
            if len(solutions) == 0:
                solutions.append(f"+{','.join(moves)}{comment}")
                has_correct_answer = True
            elif len(solutions) == 1:
                solutions.append(f"-{','.join(moves)}{comment}")
            else:
                solutions.append(f"/{','.join(moves)}{comment}")
    
    if not has_correct_answer:
        raise ValueError("必須至少有一個正確答案")
    
    # 組合 SHF 格式
    shf = f"{shf_id}:{shf_size}:{','.join(setup)}{initial_comment}:{','.join(solutions)},"
    
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
    parser.add_argument("-i", "--id", help="Problem ID (5-digit number)")
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

    shf_result = sgf_to_shf(sgf_content, args.id)

    if args.output:
        with open(args.output, 'w') as file:
            file.write(shf_result)
        if args.verbose:
            print(f"SHF data has been written to {args.output}")
    else:
        print(shf_result) 