from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen, QPainterPath
from PyQt6.QtCore import Qt, QRect, QPointF
import logging

logger = logging.getLogger(__name__)

class GoBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_size = 19  # 默認19路棋盤
        self.stones = {}  # 存儲棋子位置和顏色
        self.last_move = None  # 最後一手的位置
        self.is_initial_setup = True  # 是否正在設置初始棋盤
        self.setMinimumSize(600, 600)
        self.margin = 40  # 邊距
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def clear(self):
        """清空棋盤"""
        self.stones.clear()
        self.last_move = None
        self.is_initial_setup = True
        self.update()
        
    def get_neighbors(self, x, y):
        """獲取指定位置的相鄰點"""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                neighbors.append((nx, ny))
        return neighbors
        
    def get_group_liberties(self, x, y, visited=None):
        """獲取一個棋子群的氣"""
        if visited is None:
            visited = set()
            
        if (x, y) not in self.stones:
            return set()
            
        color = self.stones[(x, y)]
        liberties = set()
        group = set()
        
        def find_liberties(x, y):
            if (x, y) in visited:
                return
            visited.add((x, y))
            
            if (x, y) not in self.stones:
                liberties.add((x, y))
                return
                
            if self.stones[(x, y)] != color:
                return
                
            group.add((x, y))
            for nx, ny in self.get_neighbors(x, y):
                find_liberties(nx, ny)
                
        find_liberties(x, y)
        return liberties
        
    def remove_dead_stones(self, x, y):
        """移除死棋"""
        if (x, y) not in self.stones:
            return set()
            
        color = self.stones[(x, y)]
        opponent_color = "white" if color == "black" else "black"
        removed_stones = set()
        
        # 檢查四周的對方棋子群
        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) in self.stones and self.stones[(nx, ny)] == opponent_color:
                # 如果對方棋子群沒有氣，則移除
                if not self.get_group_liberties(nx, ny):
                    # 找出整個無氣的棋子群
                    dead_group = set()
                    visited = set()
                    
                    def find_group(x, y):
                        if (x, y) in visited or (x, y) not in self.stones:
                            return
                        visited.add((x, y))
                        if self.stones[(x, y)] == opponent_color:
                            dead_group.add((x, y))
                            for nx, ny in self.get_neighbors(x, y):
                                find_group(nx, ny)
                                
                    find_group(nx, ny)
                    
                    # 移除死棋
                    for dx, dy in dead_group:
                        del self.stones[(dx, dy)]
                        removed_stones.add((dx, dy))
                        
        return removed_stones
        
    def place_stone(self, pos, color):
        """在指定位置放置棋子"""
        try:
            x, y = self._convert_pos(pos)
            if not self._is_valid_pos(x, y):
                return False
            
            # 如果位置已經有棋子，則返回
            if (x, y) in self.stones:
                return False
                
            # 先放置棋子
            self.stones[(x, y)] = color
            
            # 檢查是否提子
            removed_stones = self.remove_dead_stones(x, y)
            
            # 如果沒有提子，且這手棋沒有氣（自殺手），則撤銷此手
            if not removed_stones and not self.get_group_liberties(x, y):
                del self.stones[(x, y)]
                self.last_move = None
                return False
                
            # 只有在不是初始設置時才標記最後落子
            if not self.is_initial_setup:
                self.last_move = (x, y)
            self.update()
            return True
        except ValueError:
            return False
        
    def set_initial_stones_complete(self):
        """標記初始棋盤設置完成"""
        self.is_initial_setup = False
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 計算棋盤格子大小
        board_width = min(self.width(), self.height()) - 2 * self.margin
        grid_size = board_width / (self.board_size - 1)
        
        # 計算棋盤實際區域
        board_rect = QRect(
            self.margin,
            self.margin,
            int(grid_size * (self.board_size - 1)),
            int(grid_size * (self.board_size - 1))
        )
        
        # 繪製棋盤背景（稍大於實際區域，形成邊框效果）
        background_rect = QRect(
            int(board_rect.left() - grid_size/3),
            int(board_rect.top() - grid_size/3),
            int(board_rect.width() + grid_size*2/3),
            int(board_rect.height() + grid_size*2/3)
        )
        painter.fillRect(background_rect, QColor(240, 200, 150))  # 木紋色
        
        # 繪製外框
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(board_rect)
        
        # 繪製網格線
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        for i in range(self.board_size):
            # 豎線
            x = int(self.margin + i * grid_size)
            painter.drawLine(
                x, board_rect.top(),
                x, board_rect.bottom()
            )
            # 橫線
            y = int(self.margin + i * grid_size)
            painter.drawLine(
                board_rect.left(), y,
                board_rect.right(), y
            )
            
        # 繪製星位
        star_points = [
            (3, 3), (3, 9), (3, 15),
            (9, 3), (9, 9), (9, 15),
            (15, 3), (15, 9), (15, 15)
        ]
        for x, y in star_points:
            if x < self.board_size and y < self.board_size:
                center_x = int(self.margin + x * grid_size)
                center_y = int(self.margin + y * grid_size)
                painter.setBrush(Qt.GlobalColor.black)
                painter.drawEllipse(
                    QPointF(center_x, center_y),
                    3, 3
                )
                
        # 繪製棋子
        stone_size = grid_size * 0.45  # 棋子大小
        for (x, y), color in self.stones.items():
            center_x = int(self.margin + x * grid_size)
            center_y = int(self.margin + y * grid_size)
            
            # 設置陰影
            shadow = QRadialGradient(
                center_x, center_y,
                stone_size * 1.2
            )
            shadow.setColorAt(0, QColor(0, 0, 0, 30))
            shadow.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(shadow)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                QPointF(center_x + 2, center_y + 2),  # 稍微偏移陰影
                stone_size,
                stone_size
            )
            
            # 創建主體漸變效果
            gradient = QRadialGradient(
                center_x, center_y,
                stone_size
            )
            if color == "black":
                # 黑棋使用更深的黑色和微弱的藍色調
                gradient.setColorAt(0, QColor(50, 50, 55))
                gradient.setColorAt(0.4, QColor(30, 30, 35))
                gradient.setColorAt(1, QColor(10, 10, 15))
                
                # 添加邊緣
                painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
            else:
                # 白棋使用暖色調
                gradient.setColorAt(0, QColor(255, 255, 253))
                gradient.setColorAt(0.4, QColor(250, 250, 246))
                gradient.setColorAt(1, QColor(230, 230, 225))
                
                # 添加邊緣
                painter.setPen(QPen(QColor(180, 180, 180, 100), 1))
                
            painter.setBrush(gradient)
            painter.drawEllipse(
                QPointF(center_x, center_y),
                stone_size,
                stone_size
            )
            
            # 添加高光效果（更微妙）
            highlight = QRadialGradient(
                center_x - stone_size * 0.2,  # 調整高光位置
                center_y - stone_size * 0.2,
                stone_size * 0.7  # 縮小高光範圍
            )
            if color == "black":
                # 黑棋的高光更微弱
                highlight.setColorAt(0, QColor(255, 255, 255, 40))
                highlight.setColorAt(0.5, QColor(255, 255, 255, 10))
                highlight.setColorAt(1, QColor(255, 255, 255, 0))
            else:
                # 白棋的高光更明顯
                highlight.setColorAt(0, QColor(255, 255, 255, 60))
                highlight.setColorAt(0.5, QColor(255, 255, 255, 30))
                highlight.setColorAt(1, QColor(255, 255, 255, 0))
                
            painter.setBrush(highlight)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                QPointF(center_x - stone_size * 0.2,
                       center_y - stone_size * 0.2),
                stone_size * 0.5,
                stone_size * 0.5
            )
            
            # 如果是最後落子且不是在初始設置階段，添加三角形標記
            if self.last_move and (x, y) == self.last_move and not self.is_initial_setup:
                # 計算三角形的三個頂點
                triangle_size = stone_size * 0.95  # 調整三角形尺寸為棋子大小的95%
                
                # 計算三角形的三個頂點（西北為直角）
                points = [
                    QPointF(center_x, center_y),  # 直角點（中心點）
                    QPointF(center_x + triangle_size, center_y),  # 右點（貼著棋子右側）
                    QPointF(center_x, center_y + triangle_size)   # 下點（貼著棋子下方）
                ]
                
                # 設置三角形顏色（與棋子顏色相反）
                triangle_color = Qt.GlobalColor.white if color == "black" else Qt.GlobalColor.black
                painter.setBrush(triangle_color)
                painter.setPen(QPen(triangle_color, 2))
                
                # 繪製三角形
                path = QPainterPath()
                path.moveTo(points[0])
                path.lineTo(points[1])
                path.lineTo(points[2])
                path.lineTo(points[0])
                painter.drawPath(path)

    def _convert_pos(self, pos):
        """將字符串座標轉換為數字座標"""
        if len(pos) != 2:
            raise ValueError("無效的座標格式")
        x = ord(pos[0].lower()) - ord('a')
        y = ord(pos[1].lower()) - ord('a')
        return x, y

    def _is_valid_pos(self, x, y):
        """檢查座標是否有效"""
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def _is_suicide(self, x, y, color):
        """檢查是否是自殺手"""
        # 先假設放置棋子
        self.stones[(x, y)] = color
        
        # 檢查是否有氣
        has_liberties = bool(self.get_group_liberties(x, y))
        
        # 移除假設的棋子
        del self.stones[(x, y)]
        
        return not has_liberties 