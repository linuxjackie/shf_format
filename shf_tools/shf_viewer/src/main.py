import sys
import json
import logging
import traceback
import tempfile
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QFileDialog, QPushButton, QTextEdit,
                            QMessageBox)
from PyQt6.QtCore import Qt
from board_widget import GoBoard
from shf_parser import SHFParser

def setup_logging():
    try:
        # 使用程序目錄作為日誌目錄
        script_dir = Path(__file__).parent.parent
        log_dir = script_dir / "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 創建日誌文件
        log_file = log_dir / "shf_viewer.log"
        
        # 配置日誌
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', mode='w'),
                logging.StreamHandler(sys.stdout)  # 確保輸出到控制台
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"日誌文件位置: {log_file}")
        
        # 立即寫入一條測試日誌
        logger.info("日誌系統初始化成功")
        
        return logger
    except Exception as e:
        # 如果出錯，打印到控制台
        print(f"設置日誌系統時出錯: {str(e)}")
        print(f"錯誤詳情: {traceback.format_exc()}")
        
        # 使用基本配置
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        return logging.getLogger(__name__)

# 在程式開始時立即設置日誌系統
try:
    logger = setup_logging()
    logger.info("程式啟動")
except Exception as e:
    print(f"初始化日誌系統失敗: {str(e)}")

class SHFViewer(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            logger.info("初始化 SHF Viewer...")
            
            self.setWindowTitle("SHF Viewer")
            self.setMinimumSize(1200, 800)
            
            # 主要佈局
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QHBoxLayout(main_widget)
            
            # 左側棋盤區域
            logger.debug("創建棋盤組件...")
            self.board = GoBoard()
            layout.addWidget(self.board, stretch=2)
            
            # 右側區域
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            layout.addWidget(right_panel, stretch=1)
            
            # 載入按鈕
            load_button = QPushButton("載入SHF文件")
            load_button.clicked.connect(self.load_shf)
            right_layout.addWidget(load_button)
            
            # 注釋框
            self.initial_comment = QTextEdit()
            self.initial_comment.setReadOnly(True)
            self.initial_comment.setPlaceholderText("初始注釋")
            right_layout.addWidget(self.initial_comment)
            
            self.answer_comment = QTextEdit()
            self.answer_comment.setReadOnly(True)
            self.answer_comment.setPlaceholderText("答案注釋")
            right_layout.addWidget(self.answer_comment)
            
            # 答案控制按鈕
            control_layout = QHBoxLayout()
            self.prev_button = QPushButton("上一步")
            self.next_button = QPushButton("下一步")
            self.prev_var_button = QPushButton("上一個變化")
            self.next_var_button = QPushButton("下一個變化")
            self.clear_button = QPushButton("清除棋盤")
            
            self.prev_button.clicked.connect(self.prev_move)
            self.next_button.clicked.connect(self.next_move)
            self.prev_var_button.clicked.connect(self.prev_variation)
            self.next_var_button.clicked.connect(self.next_variation)
            self.clear_button.clicked.connect(self.clear_board)
            
            control_layout.addWidget(self.prev_button)
            control_layout.addWidget(self.next_button)
            control_layout.addWidget(self.prev_var_button)
            control_layout.addWidget(self.next_var_button)
            control_layout.addWidget(self.clear_button)
            right_layout.addLayout(control_layout)
            
            # 初始化解析器
            self.parser = None
            self.current_path = None
            self.current_move_index = -1
            
            logger.info("SHF Viewer 初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失敗: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        
    def load_shf(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "選擇SHF文件",
                "",
                "SHF Files (*.shf);;All Files (*)"
            )
            if file_name:
                logger.info(f"載入文件: {file_name}")
                self.parser = SHFParser(file_name)
                self.current_move_index = -1
                self.update_board()
                self.initial_comment.setText(self.parser.initial_comment)
                logger.info("文件載入成功")
                
        except Exception as e:
            logger.error(f"載入文件失敗: {str(e)}")
            logger.error(traceback.format_exc())
            
    def update_board(self):
        try:
            if not self.parser:
                return
                
            logger.debug("更新棋盤...")
            # 清空棋盤
            self.board.clear()
            
            # 設置初始狀態
            for stone in self.parser.initial_state:
                color = "black" if stone.startswith("B") else "white"
                pos = stone[1:]
                self.board.place_stone(pos, color)
                logger.debug(f"放置棋子: {color} at {pos}")

            # 標記初始棋盤設置完成
            self.board.set_initial_stones_complete()
                
            # 顯示到當前移動的所有步驟
            if self.current_move_index >= 0:
                current_path = self.parser.get_current_path()
                for i, move in enumerate(current_path[:self.current_move_index + 1]):
                    color = "black" if move.startswith("B") else "white"
                    pos = move[1:]
                    self.board.place_stone(pos, color)
                    logger.debug(f"放置移動: {color} at {pos}")
                    
                # 如果是最後一步，顯示注釋
                if self.current_move_index == len(current_path) - 1:
                    self.answer_comment.setText(self.parser.get_current_comment())
                else:
                    self.answer_comment.clear()
                    
            logger.debug("棋盤更新完成")
            
        except Exception as e:
            logger.error(f"更新棋盤失敗: {str(e)}")
            logger.error(traceback.format_exc())
            
    def next_move(self):
        try:
            if not self.parser:
                return
                
            current_path = self.parser.get_current_path()
            if self.current_move_index >= len(current_path) - 1:
                QMessageBox.information(self, "提示", "這是最後一手了！")
                return
                
            self.current_move_index += 1
            logger.debug(f"下一步: {self.current_move_index}")
            self.update_board()
                
        except Exception as e:
            logger.error(f"下一步失敗: {str(e)}")
            logger.error(traceback.format_exc())
            
    def prev_move(self):
        try:
            if not self.parser:
                return
                
            if self.current_move_index <= 0:
                QMessageBox.information(self, "提示", "這是第一手！")
                return
                
            self.current_move_index -= 1
            logger.debug(f"上一步: {self.current_move_index}")
            self.update_board()
            
        except Exception as e:
            logger.error(f"上一步失敗: {str(e)}")
            logger.error(traceback.format_exc())

    def clear_board(self):
        """清除棋盤並重置狀態"""
        try:
            logger.info("清除棋盤...")
            self.board.clear()
            self.current_move_index = -1
            self.initial_comment.clear()
            self.answer_comment.clear()
            logger.info("棋盤清除完成")
        except Exception as e:
            logger.error(f"清除棋盤失敗: {str(e)}")
            logger.error(traceback.format_exc())

    def next_variation(self):
        """切換到下一個答案序列"""
        try:
            if not self.parser:
                return
                
            if self.parser.current_answer_index >= len(self.parser.answers) - 1:
                QMessageBox.information(self, "提示", "這是最後面的變化了！")
                return
                
            if self.parser.next_variation():
                # 清除當前狀態
                self.board.clear()
                self.current_move_index = -1
                self.answer_comment.clear()
                
                # 重新設置初始狀態
                self.update_board()
                logger.debug("切換到下一個變化")
                
        except Exception as e:
            logger.error(f"切換到下一個變化失敗: {str(e)}")
            logger.error(traceback.format_exc())
            
    def prev_variation(self):
        """切換到上一個答案序列"""
        try:
            if not self.parser:
                return
                
            if self.parser.current_answer_index <= 0:
                QMessageBox.information(self, "提示", "這是最前面的變化了！")
                return
                
            if self.parser.prev_variation():
                # 清除當前狀態
                self.board.clear()
                self.current_move_index = -1
                self.answer_comment.clear()
                
                # 重新設置初始狀態
                self.update_board()
                logger.debug("切換到上一個變化")
                
        except Exception as e:
            logger.error(f"切換到上一個變化失敗: {str(e)}")
            logger.error(traceback.format_exc())

def main():
    try:
        logger.info("正在初始化 Qt 應用程序...")
        
        # 確保只有一個 QApplication 實例
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        logger.info("創建主窗口...")
        viewer = SHFViewer()
        viewer.show()
        
        logger.info("進入應用程序主循環")
        sys.exit(app.exec())
        
    except Exception as e:
        error_msg = f"應用程序啟動失敗: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        
        # 顯示錯誤對話框
        if QApplication.instance():
            QMessageBox.critical(None, "錯誤", error_msg)
        else:
            print(error_msg)
        
        sys.exit(1)

if __name__ == "__main__":
    main() 