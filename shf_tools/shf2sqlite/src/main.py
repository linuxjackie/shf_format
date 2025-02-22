import sys
import os
import logging
import traceback
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QFileDialog, QPushButton, QTextEdit,
                            QLabel, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sqlite3
import re

def setup_logging():
    try:
        script_dir = Path(__file__).parent.parent
        log_dir = script_dir / "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = log_dir / "shf2sqlite.log"
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', mode='w'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"日誌文件位置: {log_file}")
        logger.info("日誌系統初始化成功")
        
        return logger
    except Exception as e:
        print(f"設置日誌系統時出錯: {str(e)}")
        print(f"錯誤詳情: {traceback.format_exc()}")
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        return logging.getLogger(__name__)

logger = setup_logging()

def setup_database(db_path):
    """設置數據庫結構"""
    try:
        # 如果數據庫文件已存在，先刪除它
        if os.path.exists(db_path):
            os.remove(db_path)
            
        # 創建新的數據庫連接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 創建表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id TEXT PRIMARY KEY,
                level TEXT NOT NULL,
                size INTEGER NOT NULL,
                initial_comment TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS initial_positions (
                game_id TEXT,
                color TEXT NOT NULL CHECK (color IN ('B', 'W')),
                position TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                game_id TEXT,
                answer_type TEXT NOT NULL CHECK (answer_type IN ('+', '-', '/')),
                moves TEXT NOT NULL,
                comment TEXT,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        """)
        
        conn.commit()
        return conn, cursor
    except Exception as e:
        logger.error(f"設置數據庫時出錯: {str(e)}")
        raise

def validate_position(position):
    """驗證棋子位置是否有效"""
    return bool(re.match(r'^[a-s]{2}$', position))

def _parse_answer(answer_str):
    """解析答案字符串"""
    if not answer_str or answer_str.isspace():
        return None
        
    # 清理字符串
    answer_str = answer_str.strip()
    if not answer_str:
        return None
        
    # 第一個字符是答案類型
    answer_type = answer_str[0]
    if answer_type not in ['+', '-', '/']:
        # 嘗試從字符串中找到有效的答案類型
        for char in answer_str:
            if char in ['+', '-', '/']:
                answer_type = char
                answer_str = char + answer_str[answer_str.index(char) + 1:]
                break
        else:
            raise ValueError(f"無效的答案類型：{answer_type}")
        
    # 檢查是否有注釋
    remaining = answer_str[1:]
    if '#' in remaining:
        moves, comment = remaining.split('#', 1)
        # 移除注釋末尾的逗號和空白
        comment = comment.strip().rstrip(',')
    else:
        moves = remaining
        comment = ""
        
    # 清理和驗證移動序列
    moves = moves.strip().rstrip(',')
    if moves:
        valid_moves = []
        for move in moves.split(','):
            move = move.strip()
            if move:
                # 檢查移動格式
                if len(move) >= 3 and move[0] in 'BW':
                    pos = move[1:].lower()
                    if validate_position(pos):
                        valid_moves.append(f"{move[0]}{pos}")
                    else:
                        raise ValueError(f"無效的棋子位置：{pos}")
                else:
                    raise ValueError(f"無效的移動格式：{move}")
        moves = ','.join(valid_moves)
    
    return {
        'type': answer_type,
        'moves': moves,
        'comment': comment
    }

def parse_shf_line(line):
    """解析 SHF 格式行"""
    parts = line.strip().split(':')
    if len(parts) < 5:
        raise ValueError("無效的 SHF 格式：缺少必要部分")
    
    # 解析級別
    level = parts[0]
    if level == "00":
        pass  # 未標示級別
    elif level.endswith('d'):
        if not (1 <= int(level[:-1]) <= 9):
            raise ValueError(f"無效的段位格式：{level}")
    elif level.endswith('k'):
        if not (1 <= int(level[:-1]) <= 30):
            raise ValueError(f"無效的級位格式：{level}")
    else:
        raise ValueError(f"無效的級別格式：{level}")
    
    # 解析 ID
    id_str = parts[1]
    if not re.match(r'^\d{5}$', id_str):
        raise ValueError(f"無效的 ID 格式：{id_str}")
    
    # 解析棋盤大小
    size_code = parts[2]
    if size_code == '1':
        board_size = 9
    elif size_code == '2':
        board_size = 13
    elif size_code == '3':
        board_size = 19
    else:
        raise ValueError(f"無效的棋盤大小代碼：{size_code}")
    
    # 解析初始狀態和注釋
    initial_part = parts[3]
    if '#' in initial_part:
        initial_state, initial_comment = initial_part.split('#', 1)
    else:
        initial_state = initial_part
        initial_comment = ""
    
    initial_positions = []
    for pos in initial_state.split(','):
        if pos:
            if len(pos) < 3 or pos[0] not in 'BW' or not re.match(r'^[a-s]{2}$', pos[1:]):
                raise ValueError(f"無效的棋子位置：{pos}")
            initial_positions.append({
                'color': pos[0],
                'position': pos[1:]
            })
    
    # 解析答案序列
    answers_part = parts[4]
    answers = []
    current_answer = ""
    
    for char in answers_part:
        if char in ['+', '-', '/'] and current_answer:
            if current_answer:
                answers.append(_parse_answer(current_answer))
            current_answer = char
        else:
            current_answer += char
    
    if current_answer:
        answers.append(_parse_answer(current_answer))
    
    return {
        'level': level,
        'id': id_str,
        'size': board_size,
        'initial_comment': initial_comment,
        'initial_positions': initial_positions,
        'answers': answers
    }

class ConversionWorker(QThread):
    """處理數據庫轉換的工作線程"""
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    conversion_finished = pyqtSignal()
    error_occurred = pyqtSignal(str, str)  # 修改為發送標題和消息

    def __init__(self, input_files, db_path):
        super().__init__()
        self.input_files = input_files
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            # 初始化數據庫
            conn, cursor = setup_database(self.db_path)
            
            total_files = len(self.input_files)
            processed_files = 0
            
            for file_path in self.input_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        
                    # 解析 SHF 文件
                    game_data = parse_shf_line(content)
                    
                    # 驗證所有位置
                    for pos in game_data['initial_positions']:
                        if not validate_position(pos['position']):
                            raise ValueError(f"無效的棋子位置：{pos['position']}")
                    
                    # 插入遊戲數據
                    cursor.execute("""
                        INSERT INTO games (id, level, size, initial_comment)
                        VALUES (?, ?, ?, ?)
                    """, (game_data['id'], game_data['level'], game_data['size'], game_data['initial_comment']))
                    
                    # 插入初始位置
                    for pos in game_data['initial_positions']:
                        cursor.execute("""
                            INSERT INTO initial_positions (game_id, color, position)
                            VALUES (?, ?, ?)
                        """, (game_data['id'], pos['color'], pos['position']))
                    
                    # 插入答案
                    for answer in game_data['answers']:
                        cursor.execute("""
                            INSERT INTO answers (game_id, answer_type, moves, comment)
                            VALUES (?, ?, ?, ?)
                        """, (game_data['id'], answer['type'], answer['moves'], answer.get('comment', '')))
                    
                    processed_files += 1
                    progress = int((processed_files / total_files) * 100)
                    self.progress_updated.emit(progress)
                    self.log_message.emit(f"已處理: {file_path}")
                    
                except Exception as e:
                    self.log_message.emit(f"處理文件 {file_path} 時出錯: {str(e)}")
                    logger.error(f"處理文件 {file_path} 時出錯: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            self.conversion_finished.emit()
            
        except Exception as e:
            error_msg = f"轉換過程中發生錯誤: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            self.error_occurred.emit("錯誤", error_msg)

class SHF2SQLiteConverter(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            logger.info("初始化 SHF2SQLite 轉換器...")
            
            self.setWindowTitle("SHF to SQLite 轉換器")
            self.setMinimumSize(800, 600)
            
            # 主要佈局
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout(main_widget)
            
            # 文件選擇區域
            file_layout = QHBoxLayout()
            self.input_label = QLabel("已選擇文件:")
            self.input_files = QTextEdit()
            self.input_files.setMaximumHeight(100)
            self.input_files.setReadOnly(True)
            self.browse_button = QPushButton("選擇文件")
            self.browse_button.clicked.connect(self.browse_files)
            
            file_layout.addWidget(self.input_label)
            file_layout.addWidget(self.input_files)
            file_layout.addWidget(self.browse_button)
            layout.addLayout(file_layout)
            
            # 輸出數據庫選擇
            output_layout = QHBoxLayout()
            self.output_label = QLabel("輸出數據庫:")
            self.output_path = QTextEdit()
            self.output_path.setMaximumHeight(30)
            self.output_path.setReadOnly(True)
            self.save_button = QPushButton("選擇保存位置")
            self.save_button.clicked.connect(self.select_save_location)
            
            output_layout.addWidget(self.output_label)
            output_layout.addWidget(self.output_path)
            output_layout.addWidget(self.save_button)
            layout.addLayout(output_layout)
            
            # 進度條
            self.progress_bar = QProgressBar()
            layout.addWidget(self.progress_bar)
            
            # 轉換按鈕
            self.convert_button = QPushButton("開始轉換")
            self.convert_button.clicked.connect(self.start_conversion)
            self.convert_button.setEnabled(False)
            layout.addWidget(self.convert_button)
            
            # 日誌顯示區域
            self.log_display = QTextEdit()
            self.log_display.setReadOnly(True)
            layout.addWidget(self.log_display)
            
            # 存儲選擇的文件
            self.selected_files = []
            
            logger.info("SHF2SQLite 轉換器初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失敗: {str(e)}")
            logger.error(traceback.format_exc())
            self.show_error("初始化失敗", str(e))

    def browse_files(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "選擇SHF文件",
                "",
                "SHF Files (*.shf);;All Files (*)"
            )
            if files:
                self.selected_files = files
                self.input_files.setText("\n".join(files))
                self.update_convert_button()
                logger.info(f"選擇了 {len(files)} 個文件")
                
        except Exception as e:
            logger.error(f"選擇文件失敗: {str(e)}")
            self.show_error("選擇文件失敗", str(e))
            
    def select_save_location(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "選擇保存位置",
                "",
                "SQLite Database (*.db);;All Files (*)"
            )
            if file_name:
                self.output_path.setText(file_name)
                self.update_convert_button()
                logger.info(f"選擇輸出數據庫: {file_name}")
                
        except Exception as e:
            logger.error(f"選擇保存位置失敗: {str(e)}")
            self.show_error("選擇保存位置失敗", str(e))
            
    def update_convert_button(self):
        """更新轉換按鈕的狀態"""
        self.convert_button.setEnabled(
            bool(self.selected_files) and 
            bool(self.output_path.toPlainText())
        )
        
    def start_conversion(self):
        try:
            if not self.selected_files:
                self.show_error("錯誤", "請選擇輸入文件")
                return
                
            output_file = self.output_path.toPlainText()
            if not output_file:
                self.show_error("錯誤", "請選擇輸出文件位置")
                return
                
            # 禁用按鈕
            self.convert_button.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.save_button.setEnabled(False)
            
            # 創建並啟動轉換線程
            self.worker = ConversionWorker(self.selected_files, output_file)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.log_message.connect(self.append_log)
            self.worker.conversion_finished.connect(self.conversion_finished)
            self.worker.error_occurred.connect(self.show_error)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"啟動轉換失敗: {str(e)}")
            logger.error(traceback.format_exc())
            self.show_error("啟動轉換失敗", str(e))
            
    def update_progress(self, value):
        """更新進度條"""
        self.progress_bar.setValue(value)
        
    def append_log(self, message):
        """添加日誌信息"""
        self.log_display.append(message)
        
    def conversion_finished(self):
        """轉換完成的處理"""
        self.progress_bar.setValue(100)
        self.convert_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.save_button.setEnabled(True)
        QMessageBox.information(self, "完成", "轉換完成！")
        logger.info("轉換完成")
        
    def show_error(self, title, message):
        """顯示錯誤對話框"""
        QMessageBox.critical(self, title, message)
        self.log_display.append(f"錯誤: {message}")

def main():
    try:
        logger.info("正在初始化 Qt 應用程序...")
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        logger.info("創建主窗口...")
        converter = SHF2SQLiteConverter()
        converter.show()
        
        logger.info("進入應用程序主循環")
        sys.exit(app.exec())
        
    except Exception as e:
        error_msg = f"應用程序啟動失敗: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        
        if QApplication.instance():
            QMessageBox.critical(None, "錯誤", error_msg)
        else:
            print(error_msg)
        
        sys.exit(1)

if __name__ == "__main__":
    main() 