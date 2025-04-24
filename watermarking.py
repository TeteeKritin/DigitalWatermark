import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit,
                            QGroupBox, QRadioButton, QDoubleSpinBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
import numpy as np

class WatermarkingApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Advanced Watermarking App')
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize variables
        self.host_path = ''
        self.watermark_path = ''
        self.method = 'LSB'  # Default method
        
        # Create UI
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # Left panel - Controls
        control_panel = QGroupBox("Controls")
        control_layout = QVBoxLayout()
        
        # Method selection
        method_group = QGroupBox("Watermarking Method")
        method_layout = QVBoxLayout()
        self.lsb_radio = QRadioButton("LSB (Simple)")
        self.lsb_radio.setChecked(True)
        method_layout.addWidget(self.lsb_radio)
        method_group.setLayout(method_layout)
        
        # Parameters (remove DCT parameters)
        param_group = QGroupBox("Parameters")
        param_layout = QVBoxLayout()
        param_group.setLayout(param_layout)
        
        # Image selection buttons
        self.host_button = QPushButton('Select Host Image')
        self.host_button.clicked.connect(self.select_host_image)
        
        self.watermark_button = QPushButton('Select Watermark Image')
        self.watermark_button.clicked.connect(self.select_watermark_image)
        
        # Action buttons
        self.embed_button = QPushButton('Embed Watermark')
        self.embed_button.clicked.connect(self.embed)
        self.embed_button.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.extract_button = QPushButton('Extract Watermark')
        self.extract_button.clicked.connect(self.extract)
        self.extract_button.setStyleSheet("background-color: #2196F3; color: white;")
        
        # Status log
        self.status = QTextEdit()
        self.status.setReadOnly(True)
        
        # Add widgets to control panel
        control_layout.addWidget(method_group)
        control_layout.addWidget(param_group)
        control_layout.addWidget(self.host_button)
        control_layout.addWidget(self.watermark_button)
        control_layout.addWidget(self.embed_button)
        control_layout.addWidget(self.extract_button)
        control_layout.addWidget(self.status)
        control_panel.setLayout(control_layout)
        
        # Right panel - Image display
        self.image_panel = QGroupBox("Image Preview")
        image_layout = QVBoxLayout()
        
        self.host_label = QLabel()
        self.host_label.setAlignment(Qt.AlignCenter)
        self.host_label.setStyleSheet("border: 1px solid gray;")
        
        self.watermark_label = QLabel()
        self.watermark_label.setAlignment(Qt.AlignCenter)
        self.watermark_label.setStyleSheet("border: 1px solid gray;")
        
        image_layout.addWidget(QLabel("Host Image:"))
        image_layout.addWidget(self.host_label)
        image_layout.addWidget(QLabel("Watermark Image:"))
        image_layout.addWidget(self.watermark_label)
        self.image_panel.setLayout(image_layout)
        
        # Add panels to main layout
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.image_panel, 2)
        self.setLayout(main_layout)
        
    def log(self, message):
        self.status.append(f"> {message}")
        
    def update_image_preview(self, label, image_path):
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale pixmap but maintain aspect ratio
                pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
                label.setPixmap(pixmap)
                self.log(f"Loaded: {os.path.basename(image_path)}")
            else:
                label.setText("Invalid image format")
        else:
            label.clear()
            
    def select_host_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select Host Image', '', 
            'Images (*.png *.jpg *.jpeg *.bmp)')
        if file_name:
            self.host_path = file_name
            self.update_image_preview(self.host_label, file_name)
            
    def select_watermark_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select Watermark Image', '', 
            'Images (*.png *.jpg *.jpeg *.bmp)')
        if file_name:
            self.watermark_path = file_name
            self.update_image_preview(self.watermark_label, file_name)
    
    def embed(self):
        if not self.host_path or not self.watermark_path:
            self.log("Error: Please select both host and watermark images")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Watermarked Image', '', 
            'PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)')
            
        if output_path:
            try:
                if self.lsb_radio.isChecked():
                    self.embed_lsb(self.host_path, self.watermark_path, output_path)
                self.log(f"Success! Watermarked image saved to:\n{output_path}")
            except Exception as e:
                self.log(f"Error during embedding: {str(e)}")
    
    def extract(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select Watermarked Image', '', 
            'Images (*.png *.jpg *.jpeg *.bmp)')
            
        if file_name:
            output_path, _ = QFileDialog.getSaveFileName(
                self, 'Save Extracted Watermark', '', 
                'PNG Image (*.png)')
                
            if output_path:
                try:
                    if self.lsb_radio.isChecked():
                        self.extract_lsb(file_name, output_path)
                    self.log(f"Success! Extracted watermark saved to:\n{output_path}")
                except Exception as e:
                    self.log(f"Error during extraction: {str(e)}")
    
    # Watermarking methods
    def embed_lsb(self, host_path, watermark_path, output_path):
        host_img = Image.open(host_path).convert('RGB')
        watermark_img = Image.open(watermark_path).convert('L')  # Grayscale
        
        # Resize watermark to match host dimensions
        watermark_img = watermark_img.resize(host_img.size)
        
        host_pixels = np.array(host_img)
        watermark_pixels = np.array(watermark_img)
        
        # Normalize watermark to 0-1 
        #MOre than 127 mean 1
        #less than 127 mean 0
        watermark_binary = (watermark_pixels > 127).astype(np.uint8)
        # Embed in LSB of red channel
        watermarked_pixels = host_pixels.copy()
        watermarked_pixels[:, :, 0] = (host_pixels[:, :, 0] & ~1) | watermark_binary
        
        # Save result
        Image.fromarray(watermarked_pixels).save(output_path)
    
    def extract_lsb(self, watermarked_path, output_path):
        watermarked_img = Image.open(watermarked_path).convert('RGB')
        watermarked_pixels = np.array(watermarked_img)
        
        # Extract LSB from red channel
        extracted_bits = (watermarked_pixels[:, :, 0] & 1) * 255    
        extracted_img = Image.fromarray(extracted_bits.astype(np.uint8))
        extracted_img.save(output_path)

def main():
    app = QApplication(sys.argv)
    window = WatermarkingApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
