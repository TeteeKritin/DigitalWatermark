import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit,
                            QGroupBox, QRadioButton, QSpinBox, QDoubleSpinBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image
import numpy as np
import cv2
class WatermarkingApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Advanced Watermarking App')
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize variables
        self.host_path = ''
        self.watermark_path = ''
        self.method = 'LSB'  # Default method
        self.alpha = 0.03  # DCT strength
        
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
        self.dct_radio = QRadioButton("DCT (Robust)")
        self.lsb_radio.setChecked(True)
        method_layout.addWidget(self.lsb_radio)
        method_layout.addWidget(self.dct_radio)
        method_group.setLayout(method_layout)
        
        # Parameters
        param_group = QGroupBox("Parameters")
        param_layout = QVBoxLayout()
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.01, 0.2)
        self.alpha_spin.setSingleStep(0.01)
        self.alpha_spin.setValue(0.03)
        self.alpha_spin.setPrefix("DCT Strength: ")
        param_layout.addWidget(self.alpha_spin)
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
                else:
                    self.alpha = self.alpha_spin.value()
                    self.embed_dct(self.host_path, self.watermark_path, output_path)
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
                    else:
                        original_path, _ = QFileDialog.getOpenFileName(
                            self, 'Select Original Host Image (for DCT extraction)')
                        if original_path:
                            self.alpha = self.alpha_spin.value()
                            self.extract_dct(file_name, original_path, output_path)
                        else:
                            self.log("DCT extraction requires original host image")
                            return
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
    
    def embed_dct(self, host_path, watermark_path, output_path):
        host = cv2.imread(host_path)
        watermark = cv2.imread(watermark_path, cv2.IMREAD_GRAYSCALE)
        
        # Convert to YCbCr and work on Y channel
        host_ycbcr = cv2.cvtColor(host, cv2.COLOR_BGR2YCrCb)
        y_channel = host_ycbcr[:,:,0].astype(np.float32)
        
        # Resize watermark and convert to binary
        watermark = cv2.resize(watermark, (y_channel.shape[1], y_channel.shape[0]))
        watermark_binary = (watermark > 127).astype(np.uint8)
        
        # Process in 8x8 blocks
        block_size = 8
        watermarked = y_channel.copy()
        rows, cols = y_channel.shape
        
        for i in range(0, rows, block_size):
            for j in range(0, cols, block_size):
                if i + block_size > rows or j + block_size > cols:
                    continue
                    
                block = y_channel[i:i+block_size, j:j+block_size]
                dct_block = cv2.dct(block)
                
                # Embed in mid-frequency coefficients
                coeff1 = (3, 4)
                coeff2 = (4, 3)
                avg_coeff = (dct_block[coeff1] + dct_block[coeff2]) / 2
                
                # Get the current watermark bit
                wm_bit = watermark_binary[i//block_size, j//block_size]
                
                if wm_bit:
                    dct_block[coeff1] = avg_coeff + self.alpha * abs(avg_coeff)
                    dct_block[coeff2] = avg_coeff + self.alpha * abs(avg_coeff)
                else:
                    dct_block[coeff1] = avg_coeff - self.alpha * abs(avg_coeff)
                    dct_block[coeff2] = avg_coeff - self.alpha * abs(avg_coeff)
                
                watermarked[i:i+block_size, j:j+block_size] = cv2.idct(dct_block)
        
        # Convert back to BGR
        host_ycbcr[:,:,0] = np.clip(watermarked, 0, 255)
        watermarked_bgr = cv2.cvtColor(host_ycbcr, cv2.COLOR_YCrCb2BGR)
        cv2.imwrite(output_path, watermarked_bgr)
    
    def extract_dct(self, watermarked_path, original_path, output_path):
        watermarked = cv2.imread(watermarked_path)
        original = cv2.imread(original_path)
        
        # Convert to YCbCr and get Y channels
        wm_ycbcr = cv2.cvtColor(watermarked, cv2.COLOR_BGR2YCrCb)
        orig_ycbcr = cv2.cvtColor(original, cv2.COLOR_BGR2YCrCb)
        
        wm_y = wm_ycbcr[:,:,0].astype(np.float32)
        orig_y = orig_ycbcr[:,:,0].astype(np.float32)
        
        # Process in 8x8 blocks
        block_size = 8
        rows, cols = wm_y.shape
        secret = np.zeros((rows//block_size, cols//block_size), dtype=np.uint8)
        
        for i in range(0, rows, block_size):
            for j in range(0, cols, block_size):
                if i + block_size > rows or j + block_size > cols:
                    continue
                    
                # Get both blocks
                wm_block = wm_y[i:i+block_size, j:j+block_size]
                orig_block = orig_y[i:i+block_size, j:j+block_size]
                
                # Apply DCT
                wm_dct = cv2.dct(wm_block)
                orig_dct = cv2.dct(orig_block)
                
                # Check the same coefficients
                coeff1 = (3, 4)
                coeff2 = (4, 3)
                
                # Calculate differences
                diff1 = wm_dct[coeff1] - orig_dct[coeff1]
                diff2 = wm_dct[coeff2] - orig_dct[coeff2]
                
                # Determine the bit
                if (diff1 + diff2) > 0:
                    secret[i//block_size, j//block_size] = 255
        
        # Save the extracted watermark
        cv2.imwrite(output_path, secret)

def main():
    app = QApplication(sys.argv)
    window = WatermarkingApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()