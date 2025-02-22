import re
import sgf
import random
import logging
import os
import opencc

logger = logging.getLogger(__name__)

# 創建簡體到繁體轉換器
converter = opencc.OpenCC('s2t')

def convert_to_traditional(text):
    """將簡體中文轉換為繁體中文"""
    if not text:
        return text
    return converter.convert(text)

def extract_info_from_filename(filename):
    """從文件名中提取級別和ID信息
    例如：1d00001.sgf 或 1D00001.sgf -> ('1d', '00001')
    """
    # 移除副檔名
    basename = os.path.splitext(filename)[0]
    
    # 匹配段位/級位和ID，不區分大小寫
    match = re.match(r'([1-9][dDkK]|[1-9][0-9]?[kK])(\d{5})$', basename)
    if match:
        level, id_str = match.groups()
        # 統一轉換為小寫的d/k格式
        level = level.lower()
        return level, id_str
    return None, None

def extract_level_from_comment(comment):
    """從注釋中提取級別信息"""
    if not comment:
        return "00"
    
    # 檢查段位 (1d-9d)，不區分大小寫
    dan_match = re.search(r'([1-9])[dD]', comment)
    if dan_match:
        return f"{dan_match.group(1)}d"
    
    # 檢查級位 (1k-30k)，不區分大小寫
    kyu_match = re.search(r'([1-9]|[12][0-9]|30)[kK]', comment)
    if kyu_match:
        return f"{kyu_match.group(1)}k"
    
    # 檢查數字+D格式
    dan_match2 = re.search(r'([1-9])D', comment)
    if dan_match2:
        return f"{dan_match2.group(1)}d"
    
    # 如果沒有找到級別信息，返回 "00"
    return "00"

def clean_comment(text):
    """清理注釋文本，移除特殊標記"""
    if not text:
        return text
    try:
        # 預處理：移除不成對的括號和方括號
        def balance_brackets(s, left, right):
            stack = []
            result = []
            for i, c in enumerate(s):
                if c == left:
                    stack.append(i)
                elif c == right:
                    if stack:
                        start = stack.pop()
                        result.append((start, i))
            return result

        # 處理方括號
        brackets = balance_brackets(text, '[', ']')
        # 處理圓括號（包括中文括號）
        text = text.replace('（', '(').replace('）', ')')
        parens = balance_brackets(text, '(', ')')

        # 從後向前移除配對的括號內容
        for start, end in sorted(brackets + parens, reverse=True):
            text = text[:start] + ' ' + text[end + 1:]

        # 移除特殊字符
        special_chars = ['△', '▲', '☆', '★', '○', '●', '「', '」', '『', '』']
        for char in special_chars:
            text = text.replace(char, ' ')

        # 清理空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除開頭和結尾的標點符號
        text = text.strip(' .,。，、;；')
        
        return text.strip()
    except Exception as e:
        logger.warning(f"清理注釋時發生錯誤: {str(e)}, 原文: {text}")
        # 返回一個安全的版本
        return re.sub(r'[^\w\s]', '', text).strip()

def convert_sgf_to_shf(sgf_content, filename=None):
    """將 SGF 格式轉換為 SHF 格式
    
    Args:
        sgf_content: SGF 文件內容
        filename: SGF 文件名（可選）
    """
    try:
        # 解析 SGF
        collection = sgf.parse(sgf_content)
        game = collection.children[0]
        
        # 獲取基本信息
        board_size = int(game.nodes[0].properties.get('SZ', ['19'])[0])
        initial_comment = convert_to_traditional(clean_comment(game.nodes[0].properties.get('C', [''])[0]))
        
        # 優先從文件名獲取級別和ID
        level = "00"
        id_str = None  # 初始化為 None
        
        if filename:
            file_level, file_id = extract_info_from_filename(filename)
            if file_level:
                level = file_level
            if file_id:
                id_str = file_id
        else:
            # 如果沒有文件名，從注釋中提取級別
            level = extract_level_from_comment(initial_comment)
            
        # 如果沒有從文件名獲取到ID，則生成隨機ID
        if id_str is None:
            id_str = str(random.randint(0, 99999)).zfill(5)
        
        # 轉換棋盤大小
        if board_size == 19:
            size_code = '3'
        elif board_size == 13:
            size_code = '2'
        elif board_size == 9:
            size_code = '1'
        else:
            raise ValueError(f"不支持的棋盤大小: {board_size}")
            
        # 獲取初始狀態
        initial_state = []
        root_node = game.nodes[0]
        for color in ['AB', 'AW']:  # AB=黑棋, AW=白棋
            stones = root_node.properties.get(color, [])
            for pos in stones:
                if not re.match(r'^[a-s]{2}$', pos.lower()):
                    raise ValueError(f"無效的棋子位置：{pos}")
                stone_color = 'B' if color == 'AB' else 'W'
                initial_state.append(f"{stone_color}{pos.lower()}")
                
        # 處理變化和答案
        answers = []
        
        def collect_moves(variation, is_main=True):
            moves = []
            last_comment = ""
            last_color = None  # 不預設顏色
            
            # 處理每個節點
            for node in variation.nodes:
                current_move = None
                
                # 獲取移動
                if 'B' in node.properties:
                    pos = node.properties['B'][0]
                    if pos and re.match(r'^[a-s]{2}$', pos.lower()):
                        current_move = f"B{pos.lower()}"
                        last_color = 'B'
                elif 'W' in node.properties:
                    pos = node.properties['W'][0]
                    if pos and re.match(r'^[a-s]{2}$', pos.lower()):
                        current_move = f"W{pos.lower()}"
                        last_color = 'W'
                        
                if current_move:
                    moves.append(current_move)
                    
                # 更新注釋並轉換為繁體
                if 'C' in node.properties:
                    comment = node.properties['C'][0]
                    last_comment = convert_to_traditional(clean_comment(comment))
                    
            if moves:
                move_str = ','.join(moves)
                # 根據注釋內容判斷答案類型
                answer_type = '+' if is_main else '-'  # 默認
                if last_comment:
                    if '正确' in last_comment or '正確' in last_comment:
                        answer_type = '+'
                    elif '错误' in last_comment or '錯誤' in last_comment:
                        answer_type = '-'
                    elif '变化' in last_comment or '變化' in last_comment:
                        answer_type = '/'
                    answers.append(f"{answer_type}{move_str}#{last_comment}")
                else:
                    answers.append(f"{answer_type}{move_str}")
                    
        # 處理所有變化
        for i, variation in enumerate(game.children):
            collect_moves(variation, i == 0)
            
        # 構建 SHF 格式
        parts = [
            level,
            id_str,
            size_code,
            ','.join(initial_state) + (f"#{initial_comment}" if initial_comment else ""),
            ','.join(answers) + ','  # 確保以逗號結尾
        ]
        
        shf_format = ':'.join(parts)
        
        return {
            'shf_format': shf_format,
            'level': level,
            'id': id_str,
            'size': board_size,
            'initial_state': initial_state,
            'initial_comment': initial_comment,
            'answers': answers
        }
        
    except Exception as e:
        logger.error(f"轉換失敗: {str(e)}")
        logger.error(f"SGF內容: {sgf_content}")
        raise ValueError(f"SGF轉換失敗: {str(e)}")

if __name__ == "__main__":
    # 測試用例
    test_sgf = """(;GM[1]FF[4]CA[UTF-8]AP[GoGui:1.4.9]SZ[19]
    KM[6.5]PW[White]PB[Black]C[黑先活]
    ;B[pd];W[dp];B[pq];W[dd];B[qk];W[nc];B[pf];W[pb];B[qc];W[kc]
    ;B[fq];W[cn];B[jp];W[qo];B[qp];W[po];B[nq];W[qi];B[qg];W[oi])"""
    
    # 測試大寫段位文件名
    result1 = convert_sgf_to_shf(test_sgf, "1D00001.sgf")
    print("大寫段位文件名的結果:")
    print(result1['shf_format'])
    print()
    
    # 測試小寫段位文件名
    result2 = convert_sgf_to_shf(test_sgf, "1d00001.sgf")
    print("小寫段位文件名的結果:")
    print(result2['shf_format'])
    print()
    
    # 測試大寫級位文件名
    result3 = convert_sgf_to_shf(test_sgf, "15K00123.sgf")
    print("大寫級位文件名的結果:")
    print(result3['shf_format'])
    print()
    
    # 測試小寫級位文件名
    result4 = convert_sgf_to_shf(test_sgf, "15k00123.sgf")
    print("小寫級位文件名的結果:")
    print(result4['shf_format']) 