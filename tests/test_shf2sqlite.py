import unittest
import os
import sys
import sqlite3
import tempfile

# 添加父目录到 Python 路径以导入被测试的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shf2sqlite import convert_shf_to_sqlite

class TestSHF2SQLite(unittest.TestCase):
    def setUp(self):
        # 创建测试用的 SHF 数据
        self.test_shf_data = {
            'id': '00001',
            'size': 19,
            'black_player': 'Black',
            'white_player': 'White',
            'initial_comment': '黑先活',
            'initial_state': [
                {'color': 'B', 'position': 'pd'},
                {'color': 'W', 'position': 'dp'}
            ],
            'answers': [
                {
                    'type': '+',
                    'moves': [
                        {'color': 'B', 'position': 'aa'},
                        {'color': 'W', 'position': 'bb'}
                    ],
                    'comment': '这样黑棋可以活'
                },
                {
                    'type': '-',
                    'moves': [
                        {'color': 'B', 'position': 'cc'},
                        {'color': 'W', 'position': 'dd'}
                    ],
                    'comment': '这样下会被白吃掉'
                }
            ]
        }
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
    def tearDown(self):
        # 清理临时数据库文件
        os.unlink(self.temp_db.name)
        
    def test_basic_conversion(self):
        """测试基本的 SHF 到 SQLite 的转换"""
        convert_shf_to_sqlite(self.test_shf_data, self.temp_db.name)
        
        # 验证数据库内容
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # 检查游戏信息
        cursor.execute("""
            SELECT id, size, black_player, white_player, initial_comment 
            FROM games WHERE id=?
        """, (self.test_shf_data['id'],))
        game = cursor.fetchone()
        self.assertEqual(game[0], self.test_shf_data['id'])
        self.assertEqual(game[1], self.test_shf_data['size'])
        self.assertEqual(game[2], self.test_shf_data['black_player'])
        self.assertEqual(game[3], self.test_shf_data['white_player'])
        self.assertEqual(game[4], self.test_shf_data['initial_comment'])
        
        # 检查初始状态
        cursor.execute("""
            SELECT count(*) FROM initial_positions 
            WHERE game_id=?
        """, (self.test_shf_data['id'],))
        init_count = cursor.fetchone()[0]
        self.assertEqual(init_count, len(self.test_shf_data['initial_state']))
        
        # 检查答案序列
        cursor.execute("""
            SELECT count(*), answer_type, comment 
            FROM answers 
            WHERE game_id=? 
            GROUP BY answer_type, comment
        """, (self.test_shf_data['id'],))
        answers = cursor.fetchall()
        self.assertEqual(len(answers), len(self.test_shf_data['answers']))
        
        conn.close()

    def test_comment_handling(self):
        """测试注释的处理"""
        convert_shf_to_sqlite(self.test_shf_data, self.temp_db.name)
        
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # 检查初始注释
        cursor.execute("""
            SELECT initial_comment FROM games 
            WHERE id=?
        """, (self.test_shf_data['id'],))
        initial_comment = cursor.fetchone()[0]
        self.assertEqual(initial_comment, self.test_shf_data['initial_comment'])
        
        # 检查答案注释
        for answer in self.test_shf_data['answers']:
            cursor.execute("""
                SELECT comment FROM answers 
                WHERE game_id=? AND answer_type=?
            """, (self.test_shf_data['id'], answer['type']))
            db_comment = cursor.fetchone()[0]
            self.assertEqual(db_comment, answer['comment'])
        
        conn.close()

    def test_empty_comments(self):
        """测试空注释的处理"""
        # 创建一个没有注释的测试数据
        no_comment_data = self.test_shf_data.copy()
        no_comment_data['initial_comment'] = ''
        no_comment_data['answers'][0]['comment'] = ''
        
        convert_shf_to_sqlite(no_comment_data, self.temp_db.name)
        
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # 检查初始注释
        cursor.execute("""
            SELECT initial_comment FROM games 
            WHERE id=?
        """, (no_comment_data['id'],))
        initial_comment = cursor.fetchone()[0]
        self.assertEqual(initial_comment, '')
        
        # 检查答案注释
        cursor.execute("""
            SELECT comment FROM answers 
            WHERE game_id=? AND answer_type=?
        """, (no_comment_data['id'], no_comment_data['answers'][0]['type']))
        answer_comment = cursor.fetchone()[0]
        self.assertEqual(answer_comment, '')
        
        conn.close()

    def test_id_validation(self):
        """測試 ID 格式驗證"""
        # 無效的 ID
        invalid_data = self.test_shf_data.copy()
        invalid_data['id'] = '123'  # 不是5位數
        
        with self.assertRaises(ValueError):
            convert_shf_to_sqlite(invalid_data, self.temp_db.name)
            
        # 非數字 ID
        invalid_data['id'] = 'abcde'
        with self.assertRaises(ValueError):
            convert_shf_to_sqlite(invalid_data, self.temp_db.name)

    def test_board_size_validation(self):
        """測試棋盤大小驗證"""
        # 無效的棋盤大小
        invalid_sizes = [0, 4, 10, 20]
        
        for size in invalid_sizes:
            invalid_data = self.test_shf_data.copy()
            invalid_data['size'] = size
            
            with self.assertRaises(ValueError):
                convert_shf_to_sqlite(invalid_data, self.temp_db.name)
                
        # 有效的棋盤大小
        valid_sizes = {
            1: 9,   # 9路盤
            2: 13,  # 13路盤
            3: 19   # 19路盤
        }
        
        for size_code, board_size in valid_sizes.items():
            valid_data = self.test_shf_data.copy()
            valid_data['size'] = size_code
            convert_shf_to_sqlite(valid_data, self.temp_db.name)

    def test_coordinate_validation(self):
        """測試座標有效性驗證"""
        def get_valid_coords(size_code):
            if size_code == 1:  # 9路盤
                return 'abcdefghi'
            elif size_code == 2:  # 13路盤
                return 'abcdefghijklm'
            else:  # 19路盤
                return 'abcdefghijklmnopqrs'
        
        # 測試不同棋盤大小的有效座標
        for size_code in [1, 2, 3]:
            valid_chars = get_valid_coords(size_code)
            valid_data = self.test_shf_data.copy()
            valid_data['size'] = size_code
            
            # 使用有效座標
            valid_data['initial_state'] = [
                {'color': 'B', 'position': f'{valid_chars[0]}{valid_chars[0]}'},
                {'color': 'W', 'position': f'{valid_chars[1]}{valid_chars[1]}'}
            ]
            
            # 應該可以成功轉換
            convert_shf_to_sqlite(valid_data, self.temp_db.name)
            
            # 使用無效座標
            invalid_data = valid_data.copy()
            invalid_data['initial_state'] = [
                {'color': 'B', 'position': 'zz'},  # 無效座標
                {'color': 'W', 'position': 'aa'}
            ]
            
            # 應該拋出異常
            with self.assertRaises(ValueError):
                convert_shf_to_sqlite(invalid_data, self.temp_db.name)

    def test_move_sequence_validation(self):
        """測試移動序列的有效性"""
        # 測試黑白交替
        invalid_data = self.test_shf_data.copy()
        invalid_data['answers'][0]['moves'] = [
            {'color': 'B', 'position': 'aa'},
            {'color': 'B', 'position': 'bb'}  # 連續黑棋
        ]
        
        with self.assertRaises(ValueError):
            convert_shf_to_sqlite(invalid_data, self.temp_db.name)
            
        # 測試重複落子
        invalid_data['answers'][0]['moves'] = [
            {'color': 'B', 'position': 'aa'},
            {'color': 'W', 'position': 'aa'}  # 相同位置
        ]
        
        with self.assertRaises(ValueError):
            convert_shf_to_sqlite(invalid_data, self.temp_db.name)

if __name__ == '__main__':
    unittest.main() 