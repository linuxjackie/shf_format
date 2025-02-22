class SHFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.id = ""
        self.board_size = 19
        self.initial_state = []
        self.initial_comment = ""
        self.answers = []  # [(type, moves, comment), ...]
        self.current_answer_index = 0
        
        self._parse_file()
        
    def _parse_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # 分割主要部分
        parts = content.split(':')
        if len(parts) < 4:
            raise ValueError("Invalid SHF format")
            
        # 解析ID和棋盤大小
        self.id = parts[0]
        self.board_size = int(parts[1])
        if self.board_size == 1:
            self.board_size = 9
        elif self.board_size == 2:
            self.board_size = 13
        elif self.board_size == 3:
            self.board_size = 19
            
        # 解析初始狀態和注釋
        initial_part = parts[2]
        if '#' in initial_part:
            state, comment = initial_part.split('#', 1)
            self.initial_state = [s for s in state.split(',') if s]
            self.initial_comment = comment
        else:
            self.initial_state = [s for s in initial_part.split(',') if s]
            
        # 解析答案序列
        answers_part = parts[3]
        current_answer = ""
        
        # 遍歷每個字符來正確分割答案序列
        for char in answers_part:
            if char in ['+', '-', '/'] and current_answer:  # 新答案開始
                self._add_answer(current_answer)
                current_answer = char
            else:
                current_answer += char
                
        # 添加最後一個答案
        if current_answer:
            self._add_answer(current_answer)
            
    def _add_answer(self, answer_str):
        """解析並添加一個答案序列"""
        if not answer_str or answer_str[0] not in ['+', '-', '/']:
            return
            
        answer_type = answer_str[0]
        content = answer_str[1:]
        
        if '#' in content:
            moves_str, comment = content.split('#', 1)
            # 移除最後的逗號（如果有）
            moves_str = moves_str.rstrip(',')
            moves = [m for m in moves_str.split(',') if m]
        else:
            # 移除最後的逗號（如果有）
            content = content.rstrip(',')
            moves = [m for m in content.split(',') if m]
            comment = ""
            
        if moves:  # 只有在有移動時才添加答案
            self.answers.append((answer_type, moves, comment))
                
    def get_current_path(self):
        """獲取當前答案路徑的所有移動"""
        if not self.answers:
            return []
        return self.answers[self.current_answer_index][1]
        
    def get_current_comment(self):
        """獲取當前答案的注釋"""
        if not self.answers:
            return ""
        return self.answers[self.current_answer_index][2]
        
    def next_variation(self):
        """切換到下一個變化"""
        if self.current_answer_index < len(self.answers) - 1:
            self.current_answer_index += 1
            return True
        return False
        
    def prev_variation(self):
        """切換到上一個變化"""
        if self.current_answer_index > 0:
            self.current_answer_index -= 1
            return True
        return False 