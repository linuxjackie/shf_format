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
        
        log_file = log_dir / "sqlite2shf.log"
        
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

def validate_position(position):
    """驗證棋子位置是否有效"""
    return bool(re.match(r'^[a-s]{2}$', position))

def format_shf_line(game_data):
    """將遊戲數據格式化為 SHF 格式行"""
    try:
        # 驗證必要字段
        required_fields = ['id', 'level', 'size', 'initial_positions', 'answers']
        for field in required_fields:
            if field not in game_data:
                raise ValueError(f"缺少必要字段：{field}")
        
        # 轉換棋盤大小為代碼
        if game_data['size'] == 19:
            size_code = '3'
        elif game_data['size'] == 13:
            size_code = '2'
        elif game_data['size'] == 9:
            size_code = '1'
        else:
            raise ValueError(f"不支持的棋盤大小：{game_data['size']}")
        
        # 格式化初始位置
        initial_positions = []
        for pos in game_data['initial_positions']:
            if not validate_position(pos['position']):
                raise ValueError(f"無效的棋子位置：{pos['position']}")
            initial_positions.append(f"{pos['color']}{pos['position']}")
        
        initial_part = ','.join(initial_positions)
        if game_data.get('initial_comment'):
            initial_part += f"#{game_data['initial_comment']}"
        
        # 格式化答案序列
        answer_str = ''
        for ans in game_data['answers']:
            if answer_str:
                answer_str += ','
            answer_str += ans['type'] + ans['moves']
            if ans.get('comment'):
                answer_str += f"#{ans['comment']}"
        
        # 在答案序列最後添加一個逗號
        if answer_str:
            answer_str += ','
        
        # 組合所有部分
        parts = [
            game_data['level'],
            game_data['id'],
            size_code,
            initial_part,
            answer_str
        ]
        
        return ':'.join(parts)
        
    except Exception as e:
        logger.error(f"格式化 SHF 行時出錯: {str(e)}")
        raise

class ConversionWorker(QThread):
    """處理數據庫轉換的工作線程"""
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    conversion_finished = pyqtSignal()
    error_occurred = pyqtSignal(str, str)

    def __init__(self, db_path, output_dir):
        super().__init__()
        self.db_path = db_path
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 獲取所有遊戲
            cursor.execute("""
                SELECT id, level, size, initial_comment 
                FROM games 
                ORDER BY id
            """)
            games = cursor.fetchall()
            
            total_games = len(games)
            processed_games = 0
            
            for game in games:
                try:
                    game_id, level, size, initial_comment = game
                    
                    # 獲取初始位置
                    cursor.execute("""
                        SELECT color, position 
                        FROM initial_positions 
                        WHERE game_id = ?
                        ORDER BY rowid
                    """, (game_id,))
                    initial_positions = [
                        {'color': color, 'position': position}
                        for color, position in cursor.fetchall()
                    ]
                    
                    # 獲取答案
                    cursor.execute("""
                        SELECT answer_type, moves, comment 
                        FROM answers 
                        WHERE game_id = ?
                        ORDER BY rowid
                    """, (game_id,))
                    answers = []
                    for type, moves, comment in cursor.fetchall():
                        answer = {
                            'type': type,
                            'moves': moves.strip(','),  # 移除可能的尾隨逗號
                            'comment': comment.strip(',') if comment else ''  # 移除注釋中的尾隨逗號
                        }
                        answers.append(answer)
                    
                    # 組合遊戲數據
                    game_data = {
                        'id': game_id,
                        'level': level,
                        'size': size,
                        'initial_comment': initial_comment.strip(',') if initial_comment else '',  # 移除初始注釋中的尾隨逗號
                        'initial_positions': initial_positions,
                        'answers': answers
                    }
                    
                    # 格式化為 SHF 格式
                    shf_content = format_shf_line(game_data)
                    
                    # 寫入文件（使用不帶冒號的文件名）
                    output_file = os.path.join(self.output_dir, f"{level.lower()}{game_id}.shf")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(shf_content)
                    
                    processed_games += 1
                    progress = int((processed_games / total_games) * 100)
                    self.progress_updated.emit(progress)
                    self.log_message.emit(f"已處理: {output_file}")
                    
                except Exception as e:
                    self.log_message.emit(f"處理遊戲 {game_id} 時出錯: {str(e)}")
                    logger.error(f"處理遊戲 {game_id} 時出錯: {str(e)}")
                    continue
            
            conn.close()
            self.conversion_finished.emit()
            
        except Exception as e:
            error_msg = f"轉換過程中發生錯誤: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            self.error_occurred.emit("錯誤", error_msg)

class SQLite2SHFConverter(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            logger.info("初始化 SQLite2SHF 轉換器...")
            
            self.setWindowTitle("SQLite to SHF 轉換器")
            self.setMinimumSize(800, 600)
            
            # 主要佈局
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout(main_widget)
            
            # 數據庫選擇區域
            db_layout = QHBoxLayout()
            self.db_label = QLabel("數據庫文件:")
            self.db_path = QTextEdit()
            self.db_path.setMaximumHeight(30)
            self.db_path.setReadOnly(True)
            self.browse_button = QPushButton("選擇數據庫")
            self.browse_button.clicked.connect(self.browse_database)
            
            db_layout.addWidget(self.db_label)
            db_layout.addWidget(self.db_path)
            db_layout.addWidget(self.browse_button)
            layout.addLayout(db_layout)
            
            # 輸出目錄選擇
            output_layout = QHBoxLayout()
            self.output_label = QLabel("輸出目錄:")
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
            
            logger.info("SQLite2SHF 轉換器初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失敗: {str(e)}")
            logger.error(traceback.format_exc())
            self.show_error("初始化失敗", str(e))

    def browse_database(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "選擇數據庫文件",
                "",
                "SQLite Database (*.db);;All Files (*)"
            )
            if file_name:
                self.db_path.setText(file_name)
                self.update_convert_button()
                logger.info(f"選擇數據庫文件: {file_name}")
                
        except Exception as e:
            logger.error(f"選擇數據庫文件失敗: {str(e)}")
            self.show_error("選擇數據庫文件失敗", str(e))
            
    def select_save_location(self):
        try:
            dir_name = QFileDialog.getExistingDirectory(
                self,
                "選擇保存位置"
            )
            if dir_name:
                self.output_path.setText(dir_name)
                self.update_convert_button()
                logger.info(f"選擇輸出目錄: {dir_name}")
                
        except Exception as e:
            logger.error(f"選擇保存位置失敗: {str(e)}")
            self.show_error("選擇保存位置失敗", str(e))
            
    def update_convert_button(self):
        """更新轉換按鈕的狀態"""
        self.convert_button.setEnabled(
            bool(self.db_path.toPlainText()) and 
            bool(self.output_path.toPlainText())
        )
        
    def start_conversion(self):
        try:
            db_file = self.db_path.toPlainText()
            if not db_file:
                self.show_error("錯誤", "請選擇數據庫文件")
                return
                
            output_dir = self.output_path.toPlainText()
            if not output_dir:
                self.show_error("錯誤", "請選擇輸出目錄")
                return
                
            # 確保輸出目錄存在
            os.makedirs(output_dir, exist_ok=True)
                
            # 禁用按鈕
            self.convert_button.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.save_button.setEnabled(False)
            
            # 創建並啟動轉換線程
            self.worker = ConversionWorker(db_file, output_dir)
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
        converter = SQLite2SHFConverter()
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