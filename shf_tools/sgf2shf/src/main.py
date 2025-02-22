import sys
import os
import logging
import traceback
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QFileDialog, QPushButton, QTextEdit,
                            QLabel, QMessageBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt
from sgf2shf import convert_sgf_to_shf

def setup_logging():
    try:
        script_dir = Path(__file__).parent.parent
        log_dir = script_dir / "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = log_dir / "sgf2shf.log"
        
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

class SGF2SHFConverter(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            logger.info("初始化 SGF2SHF 轉換器...")
            
            self.setWindowTitle("SGF to SHF 轉換器")
            self.setMinimumSize(800, 600)
            
            # 主要佈局
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout(main_widget)
            
            # 選擇模式（單文件/文件夾）
            mode_layout = QHBoxLayout()
            self.mode_group = QButtonGroup()
            
            self.single_file_mode = QRadioButton("單文件模式")
            self.folder_mode = QRadioButton("文件夾模式")
            self.single_file_mode.setChecked(True)
            
            self.mode_group.addButton(self.single_file_mode)
            self.mode_group.addButton(self.folder_mode)
            
            mode_layout.addWidget(self.single_file_mode)
            mode_layout.addWidget(self.folder_mode)
            mode_layout.addStretch()
            
            layout.addLayout(mode_layout)
            
            # 文件/文件夾選擇區域
            file_layout = QHBoxLayout()
            self.input_label = QLabel("輸入:")
            self.input_path = QTextEdit()
            self.input_path.setMaximumHeight(30)
            self.input_path.setReadOnly(True)
            self.browse_button = QPushButton("瀏覽")
            self.browse_button.clicked.connect(self.browse_path)
            
            file_layout.addWidget(self.input_label)
            file_layout.addWidget(self.input_path)
            file_layout.addWidget(self.browse_button)
            layout.addLayout(file_layout)
            
            # 輸出目錄區域
            output_layout = QHBoxLayout()
            self.output_label = QLabel("輸出:")
            self.output_path = QTextEdit()
            self.output_path.setMaximumHeight(30)
            self.output_path.setReadOnly(True)
            self.save_button = QPushButton("選擇保存位置")
            self.save_button.clicked.connect(self.select_save_location)
            
            output_layout.addWidget(self.output_label)
            output_layout.addWidget(self.output_path)
            output_layout.addWidget(self.save_button)
            layout.addLayout(output_layout)
            
            # 轉換按鈕
            self.convert_button = QPushButton("轉換")
            self.convert_button.clicked.connect(self.convert)
            self.convert_button.setEnabled(False)
            layout.addWidget(self.convert_button)
            
            # 日誌顯示區域
            self.log_display = QTextEdit()
            self.log_display.setReadOnly(True)
            layout.addWidget(self.log_display)
            
            # 連接信號
            self.single_file_mode.toggled.connect(self.mode_changed)
            self.folder_mode.toggled.connect(self.mode_changed)
            
            logger.info("SGF2SHF 轉換器初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失敗: {str(e)}")
            logger.error(traceback.format_exc())
            raise
            
    def mode_changed(self):
        """處理模式切換"""
        self.input_path.clear()
        self.output_path.clear()
        self.update_convert_button()
            
    def browse_path(self):
        """瀏覽文件或文件夾"""
        try:
            if self.single_file_mode.isChecked():
                file_name, _ = QFileDialog.getOpenFileName(
                    self,
                    "選擇SGF文件",
                    "",
                    "SGF Files (*.sgf);;All Files (*)"
                )
                if file_name:
                    self.input_path.setText(file_name)
                    # 自動生成輸出文件名
                    output_file = str(Path(file_name).with_suffix('.shf'))
                    self.output_path.setText(output_file)
            else:
                folder_name = QFileDialog.getExistingDirectory(
                    self,
                    "選擇包含SGF文件的文件夾"
                )
                if folder_name:
                    self.input_path.setText(folder_name)
                    # 自動生成輸出文件夾
                    output_folder = str(Path(folder_name).parent / (Path(folder_name).name + "_shf"))
                    self.output_path.setText(output_folder)
                    
            self.update_convert_button()
            logger.info(f"選擇輸入路徑: {self.input_path.toPlainText()}")
                
        except Exception as e:
            logger.error(f"選擇路徑失敗: {str(e)}")
            self.show_error("選擇路徑失敗", str(e))
            
    def select_save_location(self):
        """選擇保存位置"""
        try:
            if self.single_file_mode.isChecked():
                file_name, _ = QFileDialog.getSaveFileName(
                    self,
                    "選擇保存位置",
                    self.output_path.toPlainText(),
                    "SHF Files (*.shf);;All Files (*)"
                )
                if file_name:
                    self.output_path.setText(file_name)
            else:
                folder_name = QFileDialog.getExistingDirectory(
                    self,
                    "選擇保存文件夾",
                    self.output_path.toPlainText()
                )
                if folder_name:
                    self.output_path.setText(folder_name)
                    
            self.update_convert_button()
            logger.info(f"選擇輸出路徑: {self.output_path.toPlainText()}")
                
        except Exception as e:
            logger.error(f"選擇保存位置失敗: {str(e)}")
            self.show_error("選擇保存位置失敗", str(e))
            
    def update_convert_button(self):
        """更新轉換按鈕的狀態"""
        self.convert_button.setEnabled(
            bool(self.input_path.toPlainText()) and 
            bool(self.output_path.toPlainText())
        )
        
    def convert(self):
        """執行轉換"""
        try:
            input_path = self.input_path.toPlainText()
            output_path = self.output_path.toPlainText()
            
            if not input_path or not output_path:
                self.show_error("錯誤", "請選擇輸入和輸出路徑")
                return
                
            if self.single_file_mode.isChecked():
                # 單文件轉換
                self.convert_single_file(input_path, output_path)
            else:
                # 批量轉換
                self.convert_folder(input_path, output_path)
                
        except Exception as e:
            error_msg = f"轉換失敗: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.show_error("轉換失敗", error_msg)
            
    def convert_single_file(self, input_file, output_file):
        """轉換單個文件"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                sgf_content = f.read()
                
            # 獲取輸入文件的文件名
            input_filename = os.path.basename(input_file)
            result = convert_sgf_to_shf(sgf_content, input_filename)
            
            # 確保輸出目錄存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result['shf_format'])
                
            self.log_display.append(f"成功轉換文件:\n{input_file} -> {output_file}")
            logger.info(f"成功轉換文件: {input_file} -> {output_file}")
            
            QMessageBox.information(self, "成功", "文件轉換完成！")
            
        except Exception as e:
            raise Exception(f"轉換文件 {input_file} 失敗: {str(e)}")
            
    def convert_folder(self, input_folder, output_folder):
        """批量轉換文件夾"""
        try:
            # 確保輸出目錄存在
            os.makedirs(output_folder, exist_ok=True)
            
            # 獲取所有 SGF 文件
            sgf_files = []
            for root, _, files in os.walk(input_folder):
                for file in files:
                    if file.lower().endswith('.sgf'):
                        sgf_files.append(os.path.join(root, file))
            
            if not sgf_files:
                self.show_error("錯誤", "未找到任何 SGF 文件")
                return
                
            # 轉換每個文件
            success_count = 0
            error_count = 0
            
            for sgf_file in sgf_files:
                try:
                    # 計算相對路徑以保持目錄結構
                    rel_path = os.path.relpath(sgf_file, input_folder)
                    output_file = os.path.join(output_folder, os.path.splitext(rel_path)[0] + '.shf')
                    
                    # 確保輸出文件的目錄存在
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    # 轉換文件
                    with open(sgf_file, 'r', encoding='utf-8') as f:
                        sgf_content = f.read()
                        
                    result = convert_sgf_to_shf(sgf_content, os.path.basename(sgf_file))
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(result['shf_format'])
                        
                    success_count += 1
                    self.log_display.append(f"成功轉換: {rel_path}")
                    logger.info(f"成功轉換: {sgf_file} -> {output_file}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"轉換失敗 {rel_path}: {str(e)}"
                    self.log_display.append(error_msg)
                    logger.error(error_msg)
                    
            # 顯示結果
            result_msg = f"轉換完成！\n成功: {success_count} 個文件\n失敗: {error_count} 個文件"
            QMessageBox.information(self, "完成", result_msg)
            
        except Exception as e:
            raise Exception(f"批量轉換失敗: {str(e)}")
            
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
        converter = SGF2SHFConverter()
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