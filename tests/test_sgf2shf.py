import unittest
import os
import sys
import time
import tempfile

# 添加父目录到 Python 路径以导入被测试的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sgf2shf import convert_sgf_to_shf

class TestSGF2SHF(unittest.TestCase):
    def setUp(self):
        # 测试用的 SGF 数据
        self.test_sgf_data = "(;GM[1]FF[4]CA[UTF-8]SZ[19]PB[Black]PW[White])"
        self.complex_sgf = """(;GM[1]FF[4]CA[UTF-8]AP[GoGui:1.4.9]SZ[19]
KM[6.5]PW[White]PB[Black]
;B[pd];W[dp];B[pq];W[dd];B[qk];W[nc];B[pf];W[pb];B[qc];W[kc]
;B[fq];W[cn];B[jp];W[qo];B[qp];W[po];B[nq];W[qi];B[qg];W[oi])"""
        
    def test_basic_conversion(self):
        """测试基本的 SGF 到 SHF 的转换"""
        result = convert_sgf_to_shf(self.test_sgf_data)
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, dict))
        
    def test_game_info(self):
        """测试游戏信息是否正确转换"""
        result = convert_sgf_to_shf(self.test_sgf_data)
        self.assertEqual(result.get('size'), 19)
        self.assertEqual(result.get('black_player'), 'Black')
        self.assertEqual(result.get('white_player'), 'White')

    def test_empty_sgf(self):
        """测试空 SGF 数据"""
        with self.assertRaises(ValueError):
            convert_sgf_to_shf("")

    def test_invalid_sgf(self):
        """测试无效的 SGF 数据"""
        invalid_sgf = "(;GM[1]FF[4]CA[UTF-8]SZ[invalid])"
        with self.assertRaises(ValueError):
            convert_sgf_to_shf(invalid_sgf)

    def test_missing_required_fields(self):
        """测试缺少必需字段的 SGF"""
        incomplete_sgf = "(;FF[4])"
        with self.assertRaises(ValueError):
            convert_sgf_to_shf(incomplete_sgf)

    def test_large_sgf(self):
        """测试处理大型 SGF 文件的性能"""
        # 创建一个包含1000步的大型 SGF
        large_sgf = "(;GM[1]FF[4]CA[UTF-8]SZ[19]"
        for i in range(1000):
            large_sgf += f";B[aa];W[bb]"
        large_sgf += ")"

        start_time = time.time()
        result = convert_sgf_to_shf(large_sgf)
        end_time = time.time()

        self.assertLess(end_time - start_time, 1.0)  # 应该在1秒内完成
        self.assertGreater(len(result['moves']), 1000)

    def test_unicode_players(self):
        """测试包含 Unicode 字符的玩家名"""
        unicode_sgf = "(;GM[1]FF[4]CA[UTF-8]SZ[19]PB[李世石]PW[AlphaGo])"
        result = convert_sgf_to_shf(unicode_sgf)
        self.assertEqual(result.get('black_player'), '李世石')
        self.assertEqual(result.get('white_player'), 'AlphaGo')

    def test_file_handling(self):
        """测试文件读写操作"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sgf', delete=False) as f:
            f.write(self.complex_sgf)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                sgf_content = f.read()
            result = convert_sgf_to_shf(sgf_content)
            self.assertIsNotNone(result)
            self.assertEqual(len(result['moves']), 20)
        finally:
            os.unlink(temp_path)

    def test_shf_format_structure(self):
        """測試完整的 SHF 格式結構"""
        sgf_with_comments = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            PB[Black]PW[White]C[黑先活]
            ;B[pd]C[這是一個好手]
            ;W[dp]
            ;B[pq]C[關鍵的一手])"""
        result = convert_sgf_to_shf(sgf_with_comments)
        shf_format = result.get('shf_format')
        
        # 檢查基本結構
        parts = shf_format.split(':')
        self.assertEqual(len(parts), 4)  # ID:size:initial_state#comment:answers
        
        # 檢查 ID 格式
        self.assertTrue(parts[0].isdigit() and len(parts[0]) == 5)
        
        # 檢查棋盤大小
        self.assertIn(parts[1], ['1', '2', '3'])
        
        # 檢查初始狀態和注釋
        initial_state_comment = parts[2].split('#')
        self.assertEqual(len(initial_state_comment), 2)
        self.assertTrue(all(move.startswith(('B', 'W')) for move in initial_state_comment[0].split(',')))
        
        # 檢查答案序列
        answers = parts[3].split(',')
        self.assertTrue(answers[-1] == '')  # 確保以逗號結尾
        answers = answers[:-1]  # 移除最後的空字符串
        
        for answer in answers:
            # 檢查答案類型標記
            self.assertIn(answer[0], ['+', '-', '/'])
            # 檢查答案序列和注釋
            if '#' in answer:
                moves, comment = answer[1:].split('#')
                self.assertTrue(all(move.startswith(('B', 'W')) for move in moves.split(',')))
                self.assertTrue(len(comment) > 0)

    def test_comments_conversion(self):
        """測試注釋的轉換"""
        sgf_with_comments = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            PB[Black]PW[White]C[黑先活]
            ;B[pd]C[這是一個好手]
            ;W[dp]
            ;B[pq]C[關鍵的一手])"""
        result = convert_sgf_to_shf(sgf_with_comments)
        
        # 檢查內部數據結構
        self.assertEqual(result.get('initial_comment'), '黑先活')
        self.assertEqual(result['moves'][0].get('comment'), '這是一個好手')
        self.assertEqual(result['moves'][2].get('comment'), '關鍵的一手')
        
        # 檢查生成的 SHF 格式
        shf_format = result.get('shf_format')
        self.assertIn('#黑先活:', shf_format)
        self.assertTrue(shf_format.endswith(','))  # 確保以逗號結尾
        
        # 檢查注釋分隔符的使用
        comment_parts = shf_format.split('#')
        self.assertTrue(len(comment_parts) > 1)  # 至少有一個注釋

    def test_empty_comments(self):
        """測試空注釋的處理"""
        sgf_no_comments = "(;GM[1]FF[4]CA[UTF-8]SZ[19]PB[Black]PW[White])"
        result = convert_sgf_to_shf(sgf_no_comments)
        shf_format = result.get('shf_format')
        
        # 檢查格式結構
        parts = shf_format.split(':')
        self.assertEqual(len(parts), 4)
        
        # 確保沒有多餘的注釋標記
        self.assertNotIn('#', shf_format)
        
        # 確保以逗號結尾
        self.assertTrue(shf_format.endswith(','))

    def test_unicode_comments(self):
        """測試包含 Unicode 字符的注釋"""
        sgf_unicode = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            PB[李世石]PW[AlphaGo]C[複雜的死活題，黑先活。])"""
        result = convert_sgf_to_shf(sgf_unicode)
        self.assertEqual(result.get('initial_comment'), '複雜的死活題，黑先活。')

    def test_coordinate_format(self):
        """測試座標格式的有效性"""
        # 9路盤的有效座標
        sgf_9x9 = """(;GM[1]FF[4]CA[UTF-8]SZ[9]
            ;B[aa];W[bb];B[cc])"""
        result_9x9 = convert_sgf_to_shf(sgf_9x9)
        parts = result_9x9.get('shf_format').split(':')
        self.assertEqual(parts[1], '1')  # 確認是9路盤
        moves = parts[2].split(',')
        self.assertTrue(all(len(m[1:]) == 2 for m in moves if m))  # 確認所有座標是2字符
        self.assertTrue(all(m[1] in 'abcdefghi' for m in moves if m))  # 確認座標範圍

        # 13路盤的有效座標
        sgf_13x13 = """(;GM[1]FF[4]CA[UTF-8]SZ[13]
            ;B[aa];W[mm];B[gc])"""
        result_13x13 = convert_sgf_to_shf(sgf_13x13)
        parts = result_13x13.get('shf_format').split(':')
        self.assertEqual(parts[1], '2')  # 確認是13路盤
        moves = parts[2].split(',')
        self.assertTrue(all(m[1] in 'abcdefghijklm' for m in moves if m))

        # 19路盤的有效座標
        sgf_19x19 = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            ;B[aa];W[ss];B[jj])"""
        result_19x19 = convert_sgf_to_shf(sgf_19x19)
        parts = result_19x19.get('shf_format').split(':')
        self.assertEqual(parts[1], '3')  # 確認是19路盤
        moves = parts[2].split(',')
        self.assertTrue(all(m[1] in 'abcdefghijklmnopqrs' for m in moves if m))

    def test_invalid_coordinates(self):
        """測試無效座標的處理"""
        # 超出棋盤範圍的座標
        invalid_sgf = """(;GM[1]FF[4]CA[UTF-8]SZ[9]
            ;B[ja];W[bb])"""  # ja 在9路盤中是無效的
        with self.assertRaises(ValueError):
            convert_sgf_to_shf(invalid_sgf)

        # 格式錯誤的座標
        invalid_format_sgf = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            ;B[a];W[bb])"""  # 單字符座標是無效的
        with self.assertRaises(ValueError):
            convert_sgf_to_shf(invalid_format_sgf)

    def test_move_sequence_validation(self):
        """測試移動序列的有效性"""
        # 測試黑白交替
        invalid_sequence = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            ;B[aa];B[bb])"""  # 連續兩手黑棋是無效的
        with self.assertRaises(ValueError):
            convert_sgf_to_shf(invalid_sequence)

        # 測試重複落子
        duplicate_moves = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            ;B[aa];W[aa])"""  # 同一位置重複落子
        with self.assertRaises(ValueError):
            convert_sgf_to_shf(duplicate_moves)

    def test_answer_sequence_format(self):
        """測試答案序列的格式"""
        sgf_with_answers = """(;GM[1]FF[4]CA[UTF-8]SZ[19]C[黑先活]
            ;B[aa]C[正確答案];W[bb]
            ;B[cc]C[變化1];W[dd]
            ;B[ee]C[錯誤答案];W[ff])"""
        result = convert_sgf_to_shf(sgf_with_answers)
        shf_format = result.get('shf_format')
        
        # 檢查答案序列部分
        answers = shf_format.split(':')[3].split(',')
        answers = [a for a in answers if a]  # 移除空字符串
        
        # 檢查答案類型標記
        self.assertTrue(any(a.startswith('+') for a in answers))  # 至少有一個正確答案
        self.assertTrue(any(a.startswith('-') for a in answers))  # 至少有一個錯誤答案
        self.assertTrue(any(a.startswith('/') for a in answers))  # 至少有一個變化

        # 檢查每個答案序列的格式
        for answer in answers:
            if '#' in answer:
                moves, comment = answer[1:].split('#')
                moves = moves.split(',')
                # 檢查移動的交替順序
                self.assertTrue(all(moves[i][0] != moves[i+1][0] for i in range(len(moves)-1)))
                # 檢查座標格式
                self.assertTrue(all(len(m) == 3 and m[0] in 'BW' for m in moves))

    def test_id_format(self):
        """測試 ID 格式"""
        # ID 必須是 5 位數字
        valid_ids = ["00001", "12345", "00100"]
        invalid_ids = ["1", "123", "1234", "123456", "abcde", "0000a"]
        
        for valid_id in valid_ids:
            self.assertTrue(self._is_valid_id(valid_id))
        
        for invalid_id in invalid_ids:
            self.assertFalse(self._is_valid_id(invalid_id))
            
    def _is_valid_id(self, id_str):
        """檢查 ID 是否為有效的 5 位數字"""
        return id_str.isdigit() and len(id_str) == 5

    def test_ending_comma(self):
        """測試 SHF 格式必須以逗號結尾"""
        result = convert_sgf_to_shf(self.test_sgf_data)
        self.assertTrue(result.get('shf_format').endswith(','))
        
        # 測試多個答案序列的情況
        complex_result = convert_sgf_to_shf(self.complex_sgf)
        self.assertTrue(complex_result.get('shf_format').endswith(','))

    def test_complete_format(self):
        """測試完整的 SHF 格式"""
        result = convert_sgf_to_shf(self.complex_sgf)
        shf_format = result.get('shf_format')
        
        # 1. 檢查基本結構（四個部分）
        parts = shf_format.split(':')
        self.assertEqual(len(parts), 4)
        
        # 2. 檢查 ID
        self.assertTrue(self._is_valid_id(parts[0]))
        
        # 3. 檢查棋盤大小
        self.assertIn(parts[1], ['1', '2', '3'])
        
        # 4. 檢查初始狀態和注釋
        initial_part = parts[2]
        if '#' in initial_part:
            state, comment = initial_part.split('#')
            self.assertTrue(all(move.startswith(('B', 'W')) for move in state.split(',')))
            self.assertTrue(len(comment) > 0)
        else:
            self.assertTrue(all(move.startswith(('B', 'W')) for move in initial_part.split(',')))
        
        # 5. 檢查答案序列
        answers_part = parts[3]
        self.assertTrue(answers_part.endswith(','))
        answers = [a for a in answers_part.split(',') if a]
        
        for answer in answers:
            # 檢查答案類型標記
            self.assertIn(answer[0], ['+', '-', '/'])
            
            # 檢查答案格式
            if '#' in answer:
                moves, comment = answer[1:].split('#')
                moves = moves.split(',')
                self.assertTrue(all(move.startswith(('B', 'W')) for move in moves))
                self.assertTrue(len(comment) > 0)
            else:
                moves = answer[1:].split(',')
                self.assertTrue(all(move.startswith(('B', 'W')) for move in moves))

    def test_coordinate_validation(self):
        """測試座標驗證"""
        def validate_coordinates(size, moves):
            valid_chars = {
                '1': 'abcdefghi',      # 9路盤
                '2': 'abcdefghijklm',  # 13路盤
                '3': 'abcdefghijklmnopqrs'  # 19路盤
            }
            chars = valid_chars[size]
            return all(
                len(move) == 3 and  # B/W + 兩個座標字符
                move[0] in 'BW' and
                move[1] in chars and
                move[2] in chars
                for move in moves
            )
            
        # 測試不同棋盤大小的座標
        test_cases = [
            ('1', ['Baa', 'Wbi', 'Bcc']),  # 9路盤
            ('2', ['Baa', 'Wlm', 'Bkc']),  # 13路盤
            ('3', ['Baa', 'Wss', 'Bqq'])   # 19路盤
        ]
        
        for size, moves in test_cases:
            self.assertTrue(validate_coordinates(size, moves))
            
        # 測試無效座標
        invalid_cases = [
            ('1', ['Baa', 'Wjj', 'Bcc']),  # 9路盤不能有 'j'
            ('2', ['Baa', 'Wnn', 'Bkc']),  # 13路盤不能有 'n'
            ('3', ['Baa', 'Wtt', 'Bqq'])   # 19路盤不能有 't'
        ]
        
        for size, moves in invalid_cases:
            self.assertFalse(validate_coordinates(size, moves))

    def test_empty_initial_comment_format(self):
        """測試空初始注釋的格式"""
        sgf_no_comment = """(;GM[1]FF[4]CA[UTF-8]SZ[19]
            PB[Black]PW[White]
            ;B[pd];W[dp])"""
        result = convert_sgf_to_shf(sgf_no_comment)
        shf_format = result.get('shf_format')
        
        parts = shf_format.split(':')
        initial_state = parts[2]
        
        # 檢查沒有注釋時不應該有 # 符號
        self.assertNotIn('#', initial_state)

    def test_move_alternation(self):
        """測試移動的黑白交替"""
        # 正確的黑白交替
        valid_moves = [
            "Baa,Wbb,Bcc",  # 正確的交替
            "Waa,Bbb,Wcc",  # 白棋開始也可以
        ]
        
        # 錯誤的黑白順序
        invalid_moves = [
            "Baa,Bbb,Wcc",  # 連續黑棋
            "Waa,Wbb,Bcc",  # 連續白棋
            "Baa,Wbb,Wcc",  # 連續白棋
        ]
        
        for moves in valid_moves:
            self.assertTrue(self._is_valid_move_alternation(moves))
            
        for moves in invalid_moves:
            self.assertFalse(self._is_valid_move_alternation(moves))

    def _is_valid_move_alternation(self, moves_str):
        """檢查移動是否正確交替"""
        moves = moves_str.split(',')
        return all(moves[i][0] != moves[i+1][0] for i in range(len(moves)-1))

    def test_multiple_answer_sequences(self):
        """測試多個答案序列的組合"""
        sgf_with_multiple_answers = """(;GM[1]FF[4]CA[UTF-8]SZ[19]C[黑先活]
            ;B[aa]C[正確答案];W[bb];B[cc]
            (;W[dd];B[ee]C[變化1])
            (;W[ff];B[gg]C[錯誤答案]))"""
        result = convert_sgf_to_shf(sgf_with_multiple_answers)
        shf_format = result.get('shf_format')
        
        # 檢查答案序列部分
        answers = shf_format.split(':')[3].split(',')
        answers = [a for a in answers if a]
        
        # 確保有所有類型的答案
        answer_types = [a[0] for a in answers]
        self.assertIn('+', answer_types)  # 正確答案
        self.assertIn('-', answer_types)  # 錯誤答案
        self.assertIn('/', answer_types)  # 變化
        
        # 檢查每個答案序列的完整性
        for answer in answers:
            if '#' in answer:
                moves, comment = answer[1:].split('#')
                moves = moves.split(',')
                # 檢查黑白交替
                self.assertTrue(self._is_valid_move_alternation(','.join(moves)))
                # 檢查注釋非空
                self.assertTrue(len(comment) > 0)

    def test_answer_sequence_combinations(self):
        """測試答案序列的各種組合情況"""
        test_cases = [
            # 只有正確答案
            "+Baa,Wbb,Bcc#正確答案,",
            # 正確答案和錯誤答案
            "+Baa,Wbb,Bcc#正確答案,-Bdd,Wee,Bff#錯誤答案,",
            # 所有類型的答案
            "+Baa,Wbb#正確答案,-Bcc,Wdd#錯誤答案,/Bee,Wff#變化,",
            # 多個變化
            "+Baa,Wbb#主要答案,/Bcc,Wdd#變化1,/Bee,Wff#變化2,",
        ]
        
        for test_case in test_cases:
            # 構造完整的 SHF 格式
            shf_format = f"00001:3:Bpd,Wdp#黑先活:{test_case}"
            
            # 檢查格式
            parts = shf_format.split(':')
            self.assertEqual(len(parts), 4)  # 基本結構
            self.assertTrue(parts[3].endswith(','))  # 結尾逗號
            
            # 檢查答案序列
            answers = [a for a in parts[3].split(',') if a]
            for answer in answers:
                # 檢查答案類型標記
                self.assertIn(answer[0], ['+', '-', '/'])
                # 檢查格式
                if '#' in answer:
                    moves, comment = answer[1:].split('#')
                    self.assertTrue(self._is_valid_move_alternation(moves))
                    self.assertTrue(len(comment) > 0)

    def test_answer_sequence_rules(self):
        """測試答案序列規則"""
        # 必須至少有一個正確答案
        invalid_shf = "00001:3:Bpd,Wdp:-Baa,Wbb#錯誤1,-Bcc,Wdd#錯誤2,/Bee,Wff#變化,"
        with self.assertRaises(ValueError):
            self._validate_shf_format(invalid_shf)

        # 允許多個正確/錯誤/變化答案
        valid_combinations = [
            # 多個正確答案
            "+Baa,Wbb#正確1,+Bcc,Wdd#正確2,",
            # 多個錯誤答案
            "+Baa,Wbb#正確1,-Bcc,Wdd#錯誤1,-Bee,Wff#錯誤2,",
            # 多個變化
            "+Baa,Wbb#正確1,/Bcc,Wdd#變化1,/Bee,Wff#變化2,",
            # 混合多個答案
            "+Baa,Wbb#正確1,+Bcc,Wdd#正確2,-Bee,Wff#錯誤1,/Bgg,Whh#變化1,/Bii,Wjj#變化2,"
        ]

        for combination in valid_combinations:
            shf_format = f"00001:3:Bpd,Wdp#{combination}"
            self._validate_shf_format(shf_format)

    def test_comment_rules(self):
        """測試注釋規則"""
        valid_formats = [
            # 有初始注釋，有答案注釋
            "00001:3:Bpd,Wdp#黑先活:+Baa,Wbb#正確,",
            # 無初始注釋，有答案注釋
            "00001:3:Bpd,Wdp:+Baa,Wbb#正確,",
            # 有初始注釋，無答案注釋
            "00001:3:Bpd,Wdp#黑先活:+Baa,Wbb,",
            # 無初始注釋，無答案注釋
            "00001:3:Bpd,Wdp:+Baa,Wbb,",
            # 混合有無注釋的答案
            "00001:3:Bpd,Wdp#黑先活:+Baa,Wbb#正確,-Bcc,Wdd,/Bee,Wff#變化,"
        ]

        for format_str in valid_formats:
            self._validate_shf_format(format_str)

    def test_coordinate_rules(self):
        """測試座標規則"""
        # 測試不同棋盤大小的有效座標範圍
        board_sizes = {
            '1': 'abcdefghi',       # 9路盤
            '2': 'abcdefghijklm',   # 13路盤
            '3': 'abcdefghijklmnopqrs'  # 19路盤
        }

        for size, valid_chars in board_sizes.items():
            # 測試有效座標
            valid_moves = [f"B{c1}{c2}" for c1, c2 in zip(valid_chars[:2], valid_chars[:2])]
            shf_format = f"00001:{size}:{','.join(valid_moves)}:+{valid_moves[0]},W{valid_chars[0]}{valid_chars[1]},"
            self._validate_shf_format(shf_format)

            # 測試無效座標（超出範圍）
            next_char = chr(ord(valid_chars[-1]) + 1)
            invalid_moves = [f"B{next_char}{valid_chars[0]}"]
            invalid_format = f"00001:{size}:{','.join(invalid_moves)}:+{valid_moves[0]},"
            with self.assertRaises(ValueError):
                self._validate_shf_format(invalid_format)

            # 測試大寫座標（不允許）
            invalid_case = f"00001:{size}:BAA,Wbb:+Baa,Wbb,"
            with self.assertRaises(ValueError):
                self._validate_shf_format(invalid_case)

    def _validate_shf_format(self, shf_str):
        """驗證 SHF 格式"""
        # 基本格式檢查
        parts = shf_str.split(':')
        if len(parts) != 4:
            raise ValueError("Invalid SHF format: wrong number of parts")

        # ID 檢查
        if not self._is_valid_id(parts[0]):
            raise ValueError("Invalid ID format")

        # 棋盤大小檢查
        if parts[1] not in ['1', '2', '3']:
            raise ValueError("Invalid board size")

        # 初始狀態和注釋檢查
        initial_part = parts[2]
        if '#' in initial_part:
            state, _ = initial_part.split('#')
        else:
            state = initial_part
        self._validate_moves(state, parts[1])

        # 答案序列檢查
        answers = [a for a in parts[3].split(',') if a]
        if not any(a.startswith('+') for a in answers):
            raise ValueError("Must have at least one correct answer")

        for answer in answers:
            if not answer[0] in ['+', '-', '/']:
                raise ValueError("Invalid answer type")
            if '#' in answer:
                moves, _ = answer[1:].split('#')
            else:
                moves = answer[1:]
            self._validate_moves(moves, parts[1])

        # 添加對特殊字符的檢查
        def check_special_chars(text):
            special_chars = [':', ',', '#', '\n', '\r']
            for char in special_chars:
                if char in text:
                    raise ValueError(f"Comment contains invalid character: {char}")

        # 檢查注釋中的特殊字符
        if '#' in initial_part:
            _, comment = initial_part.split('#')
            check_special_chars(comment)

        # 檢查答案序列中的特殊字符
        for answer in answers:
            if '#' in answer:
                _, comment = answer[1:].split('#')
                check_special_chars(comment)

        # 檢查答案序列不為空
        if not answers:
            raise ValueError("Answer sequence cannot be empty")

        # 檢查移動序列長度
        for answer in answers:
            moves = answer[1:].split('#')[0].split(',')
            if len(moves) > 30:  # 假設我們限制最大步數為30
                raise ValueError("Move sequence too long")

        # 檢查重複落子
        def check_duplicate_moves(moves):
            positions = set()
            for move in moves:
                if not move:
                    continue
                pos = move[1:]
                if pos in positions:
                    raise ValueError(f"Duplicate move: {pos}")
                positions.add(pos)

        # 檢查每個答案序列中的重複落子
        for answer in answers:
            moves = answer[1:].split('#')[0].split(',')
            check_duplicate_moves(moves)

    def _validate_moves(self, moves_str, board_size):
        """驗證移動序列"""
        valid_chars = {
            '1': 'abcdefghi',
            '2': 'abcdefghijklm',
            '3': 'abcdefghijklmnopqrs'
        }[board_size]

        moves = moves_str.split(',')
        for move in moves:
            if not move:
                continue
            if len(move) != 3:
                raise ValueError(f"Invalid move format: {move}")
            if move[0] not in ['B', 'W']:
                raise ValueError(f"Invalid color: {move[0]}")
            if move[1] not in valid_chars or move[2] not in valid_chars:
                raise ValueError(f"Invalid coordinate: {move[1:]}")
            if not move[1:].islower():
                raise ValueError("Coordinates must be lowercase")

    def test_duplicate_moves_in_answer(self):
        """測試答案序列中的重複落子"""
        # 在同一個答案序列中重複落子
        invalid_answer = "00001:3:Bpd,Wdp:+Baa,Wbb,Baa,"  # Baa 重複
        with self.assertRaises(ValueError):
            self._validate_shf_format(invalid_answer)

        # 在不同答案序列中允許相同的落子
        valid_answers = "00001:3:Bpd,Wdp:+Baa,Wbb#正確答案,/Baa,Wcc#另一種變化,"
        self._validate_shf_format(valid_answers)

    def test_move_sequence_length(self):
        """測試移動序列長度限制"""
        # 生成一個超長的移動序列
        long_moves = ','.join([f"B{'ab'[i%2]}{chr(97+i)}" for i in range(50)])
        invalid_sequence = f"00001:3:Bpd,Wdp:+{long_moves},"
        
        with self.assertRaises(ValueError):
            self._validate_shf_format(invalid_sequence)

    def test_special_characters_in_comments(self):
        """測試注釋中的特殊字符"""
        special_chars = [
            "這是:一個:測試",  # 包含冒號
            "這是,一個,測試",  # 包含逗號
            "這是#一個#測試",  # 包含井號
            "這是\n一個\n測試",  # 包含換行
            "這是「測試」",  # 包含中文引號
            "這是'test'",  # 包含英文引號
        ]
        
        for comment in special_chars:
            shf_format = f"00001:3:Bpd,Wdp#{comment}:+Baa,Wbb#正確答案,"
            with self.assertRaises(ValueError):
                self._validate_shf_format(shf_format)

    def test_empty_answer_sequence(self):
        """測試空的答案序列"""
        # 完全沒有答案序列
        invalid_format = "00001:3:Bpd,Wdp:"
        with self.assertRaises(ValueError):
            self._validate_shf_format(invalid_format)

        # 只有答案類型標記但沒有實際移動
        invalid_cases = [
            "00001:3:Bpd,Wdp:+,",
            "00001:3:Bpd,Wdp:+#正確答案,",
            "00001:3:Bpd,Wdp:+Baa,Wbb,+,",  # 第二個答案序列為空
        ]
        for case in invalid_cases:
            with self.assertRaises(ValueError):
                self._validate_shf_format(case)

    def test_mixed_board_sizes(self):
        """測試混合棋盤大小的情況"""
        # 初始狀態和答案序列使用不同棋盤大小的座標
        invalid_cases = [
            # 使用19路盤座標在9路盤中
            "00001:1:Bpd,Wdp:+Baa,Wbb,",  # pd 超出9路盤範圍
            # 使用9路盤座標在19路盤中（雖然有效但不推薦）
            "00001:3:Baa,Wbb:+Bpd,Wdp,",
        ]
        
        for case in invalid_cases:
            with self.assertRaises(ValueError):
                self._validate_shf_format(case)

if __name__ == '__main__':
    unittest.main() 