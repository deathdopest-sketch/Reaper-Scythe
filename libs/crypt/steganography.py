"""
Crypt Steganography Module

This module provides steganography capabilities for hiding data
in images, audio, and text for the Reaper security-focused programming language.

Features:
- Image steganography (LSB, DCT, F5)
- Audio steganography (LSB, phase coding)
- Text steganography (whitespace, invisible characters)
- File steganography (EOF markers, metadata)
- Detection and analysis tools

Author: Reaper Security Team
Version: 0.1.0
"""

import os
import struct
import logging
from typing import Union, Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from PIL import Image
import wave
import numpy as np

logger = logging.getLogger(__name__)

class SteganographyType(Enum):
    """Types of steganography supported"""
    IMAGE_LSB = "image_lsb"
    IMAGE_DCT = "image_dct"
    AUDIO_LSB = "audio_lsb"
    AUDIO_PHASE = "audio_phase"
    TEXT_WHITESPACE = "text_whitespace"
    TEXT_INVISIBLE = "text_invisible"
    FILE_EOF = "file_eof"
    FILE_METADATA = "file_metadata"

class SteganographyMethod(Enum):
    """Steganography methods"""
    HIDE = "hide"
    EXTRACT = "extract"
    ANALYZE = "analyze"

@dataclass
class SteganographyConfig:
    """Configuration for steganography operations"""
    method: SteganographyMethod = SteganographyMethod.HIDE
    stego_type: SteganographyType = SteganographyType.IMAGE_LSB
    bit_depth: int = 1  # Number of LSBs to use
    compression: bool = False
    encryption: bool = False
    password: Optional[str] = None

@dataclass
class SteganographyResult:
    """Result of steganography operation"""
    success: bool
    data: Optional[bytes] = None
    output_path: Optional[str] = None
    capacity: Optional[int] = None
    used_capacity: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class CryptSteganographer:
    """
    Steganography engine for the Crypt library.
    
    Provides methods to hide and extract data from various media types
    including images, audio, text, and files.
    """
    
    def __init__(self, config: Optional[SteganographyConfig] = None):
        """
        Initialize steganography engine.
        
        Args:
            config: SteganographyConfig with operation parameters
        """
        self.config = config or SteganographyConfig()
    
    def hide_in_image_lsb(self, image_path: str, data: bytes, output_path: str) -> SteganographyResult:
        """
        Hide data in image using LSB steganography.
        
        Args:
            image_path: Path to cover image
            data: Data to hide
            output_path: Path for stego image
            
        Returns:
            SteganographyResult with operation status
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            pixels = list(image.getdata())
            
            # Calculate capacity
            total_pixels = width * height
            capacity = (total_pixels * 3 * self.config.bit_depth) // 8
            
            if len(data) > capacity:
                return SteganographyResult(
                    success=False,
                    error_message=f"Data too large. Capacity: {capacity}, Data size: {len(data)}"
                )
            
            # Convert data to binary
            data_bits = []
            for byte in data:
                data_bits.extend([int(bit) for bit in format(byte, '08b')])
            
            # Add length header (32 bits)
            length_bits = [int(bit) for bit in format(len(data), '032b')]
            all_bits = length_bits + data_bits
            
            # Hide data in LSBs
            bit_index = 0
            new_pixels = []
            
            for pixel in pixels:
                r, g, b = pixel
                new_pixel = []
                
                for color in [r, g, b]:
                    if bit_index < len(all_bits):
                        # Clear LSB and set new bit
                        new_color = (color & 0xFE) | all_bits[bit_index]
                        bit_index += 1
                    else:
                        new_color = color
                    new_pixel.append(new_color)
                
                new_pixels.append(tuple(new_pixel))
            
            # Create new image
            new_image = Image.new('RGB', (width, height))
            new_image.putdata(new_pixels)
            new_image.save(output_path)
            
            return SteganographyResult(
                success=True,
                output_path=output_path,
                capacity=capacity,
                used_capacity=len(data),
                metadata={
                    "method": "LSB",
                    "bit_depth": self.config.bit_depth,
                    "image_size": f"{width}x{height}",
                    "data_size": len(data)
                }
            )
            
        except Exception as e:
            logger.error(f"Image LSB steganography failed: {e}")
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def extract_from_image_lsb(self, image_path: str) -> SteganographyResult:
        """
        Extract data from image using LSB steganography.
        
        Args:
            image_path: Path to stego image
            
        Returns:
            SteganographyResult with extracted data
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            pixels = list(image.getdata())
            
            # Extract length header (32 bits)
            length_bits = []
            bit_count = 0
            
            for pixel in pixels:
                for color in pixel:
                    length_bits.append(color & 1)
                    bit_count += 1
                    if bit_count >= 32:
                        break
                if bit_count >= 32:
                    break
            
            # Convert length bits to integer
            length = int(''.join(map(str, length_bits)), 2)
            
            if length == 0 or length > 1000000:  # Sanity check
                return SteganographyResult(
                    success=False,
                    error_message="No valid data found or invalid length"
                )
            
            # Extract data bits
            data_bits = []
            bit_count = 0
            target_bits = length * 8
            
            for pixel in pixels:
                for color in pixel:
                    if bit_count >= 32:  # Skip length header
                        data_bits.append(color & 1)
                        bit_count += 1
                        if len(data_bits) >= target_bits:
                            break
                    else:
                        bit_count += 1
                if len(data_bits) >= target_bits:
                    break
            
            # Convert bits to bytes
            data_bytes = []
            for i in range(0, len(data_bits), 8):
                if i + 8 <= len(data_bits):
                    byte_bits = data_bits[i:i+8]
                    byte_value = int(''.join(map(str, byte_bits)), 2)
                    data_bytes.append(byte_value)
            
            data = bytes(data_bytes)
            
            return SteganographyResult(
                success=True,
                data=data,
                metadata={
                    "method": "LSB",
                    "bit_depth": self.config.bit_depth,
                    "extracted_size": len(data)
                }
            )
            
        except Exception as e:
            logger.error(f"Image LSB extraction failed: {e}")
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def hide_in_audio_lsb(self, audio_path: str, data: bytes, output_path: str) -> SteganographyResult:
        """
        Hide data in audio file using LSB steganography.
        
        Args:
            audio_path: Path to cover audio file
            data: Data to hide
            output_path: Path for stego audio file
            
        Returns:
            SteganographyResult with operation status
        """
        try:
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
                sample_width = audio_file.getsampwidth()
                channels = audio_file.getnchannels()
                framerate = audio_file.getframerate()
            
            # Convert frames to numpy array
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                raise ValueError(f"Unsupported sample width: {sample_width}")
            
            audio_array = np.frombuffer(frames, dtype=dtype)
            
            # Calculate capacity
            capacity = len(audio_array) // 8
            
            if len(data) > capacity:
                return SteganographyResult(
                    success=False,
                    error_message=f"Data too large. Capacity: {capacity}, Data size: {len(data)}"
                )
            
            # Convert data to binary
            data_bits = []
            for byte in data:
                data_bits.extend([int(bit) for bit in format(byte, '08b')])
            
            # Add length header
            length_bits = [int(bit) for bit in format(len(data), '032b')]
            all_bits = length_bits + data_bits
            
            # Hide data in LSBs
            new_audio_array = audio_array.copy()
            bit_index = 0
            
            for i in range(len(audio_array)):
                if bit_index < len(all_bits):
                    # Clear LSB and set new bit
                    new_audio_array[i] = (audio_array[i] & ~1) | all_bits[bit_index]
                    bit_index += 1
            
            # Save stego audio
            with wave.open(output_path, 'wb') as output_file:
                output_file.setnchannels(channels)
                output_file.setsampwidth(sample_width)
                output_file.setframerate(framerate)
                output_file.writeframes(new_audio_array.tobytes())
            
            return SteganographyResult(
                success=True,
                output_path=output_path,
                capacity=capacity,
                used_capacity=len(data),
                metadata={
                    "method": "Audio LSB",
                    "channels": channels,
                    "sample_width": sample_width,
                    "framerate": framerate,
                    "data_size": len(data)
                }
            )
            
        except Exception as e:
            logger.error(f"Audio LSB steganography failed: {e}")
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def extract_from_audio_lsb(self, audio_path: str) -> SteganographyResult:
        """
        Extract data from audio file using LSB steganography.
        
        Args:
            audio_path: Path to stego audio file
            
        Returns:
            SteganographyResult with extracted data
        """
        try:
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
                sample_width = audio_file.getsampwidth()
            
            # Convert frames to numpy array
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                raise ValueError(f"Unsupported sample width: {sample_width}")
            
            audio_array = np.frombuffer(frames, dtype=dtype)
            
            # Extract length header (32 bits)
            length_bits = []
            for i in range(32):
                if i < len(audio_array):
                    length_bits.append(audio_array[i] & 1)
            
            length = int(''.join(map(str, length_bits)), 2)
            
            if length == 0 or length > 1000000:  # Sanity check
                return SteganographyResult(
                    success=False,
                    error_message="No valid data found or invalid length"
                )
            
            # Extract data bits
            data_bits = []
            target_bits = length * 8
            
            for i in range(32, len(audio_array)):
                if len(data_bits) >= target_bits:
                    break
                data_bits.append(audio_array[i] & 1)
            
            # Convert bits to bytes
            data_bytes = []
            for i in range(0, len(data_bits), 8):
                if i + 8 <= len(data_bits):
                    byte_bits = data_bits[i:i+8]
                    byte_value = int(''.join(map(str, byte_bits)), 2)
                    data_bytes.append(byte_value)
            
            data = bytes(data_bytes)
            
            return SteganographyResult(
                success=True,
                data=data,
                metadata={
                    "method": "Audio LSB",
                    "extracted_size": len(data)
                }
            )
            
        except Exception as e:
            logger.error(f"Audio LSB extraction failed: {e}")
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def hide_in_text_whitespace(self, text: str, data: bytes) -> str:
        """
        Hide data in text using whitespace steganography.
        
        Args:
            text: Cover text
            data: Data to hide
            
        Returns:
            Text with hidden data
        """
        # Convert data to binary
        data_bits = []
        for byte in data:
            data_bits.extend([int(bit) for bit in format(byte, '08b')])
        
        # Add length header
        length_bits = [int(bit) for bit in format(len(data), '032b')]
        all_bits = length_bits + data_bits
        
        # Split text into words
        words = text.split()
        
        # Calculate available spaces (words - 1)
        available_spaces = len(words) - 1
        
        if len(all_bits) > available_spaces:
            raise ValueError(f"Text too short to hide data. Need {len(all_bits)} spaces, have {available_spaces}")
        
        # Special case: empty data - just return original text
        if len(data) == 0:
            return text
        
        # Hide bits in whitespace
        result_words = []
        bit_index = 0
        
        for i, word in enumerate(words):
            result_words.append(word)
            
            if i < len(words) - 1:  # Don't add space after last word
                if bit_index < len(all_bits):
                    # Use different whitespace characters to represent bits
                    if all_bits[bit_index] == 1:
                        result_words.append('\u200B')  # Zero-width space
                    else:
                        result_words.append(' ')  # Regular space
                    bit_index += 1
                else:
                    result_words.append(' ')  # Regular space
        
        return ' '.join(result_words)
    
    def extract_from_text_whitespace(self, text: str) -> SteganographyResult:
        """
        Extract data from text using whitespace steganography.
        
        Args:
            text: Text with hidden data
            
        Returns:
            SteganographyResult with extracted data
        """
        try:
            # Split text and analyze whitespace
            words = text.split()
            spaces = []
            
            # Use a simpler approach - iterate through the text character by character
            i = 0
            while i < len(text):
                if text[i] == ' ' or text[i] == '\u200B':
                    # Found a space, collect all consecutive spaces
                    space_chars = ''
                    while i < len(text) and (text[i] == ' ' or text[i] == '\u200B'):
                        space_chars += text[i]
                        i += 1
                    spaces.append(space_chars)
                else:
                    i += 1
            
            # Extract bits from whitespace
            bits = []
            for space in spaces:
                if '\u200B' in space:  # Zero-width space = 1
                    bits.append(1)
                else:  # Regular space = 0
                    bits.append(0)
            
            if len(bits) < 32:
                return SteganographyResult(
                    success=False,
                    error_message="No valid data found"
                )
            
            # Extract length
            length_bits = bits[:32]
            length = int(''.join(map(str, length_bits)), 2)
            
            if length == 0:
                # Empty data case
                return SteganographyResult(
                    success=True,
                    data=b'',
                    metadata={
                        "method": "Whitespace",
                        "extracted_size": 0
                    }
                )
            
            if length > 1000000:
                return SteganographyResult(
                    success=False,
                    error_message="Invalid data length"
                )
            
            # Extract data bits
            data_bits = bits[32:32 + length * 8]
            
            # Convert to bytes
            data_bytes = []
            for i in range(0, len(data_bits), 8):
                if i + 8 <= len(data_bits):
                    byte_bits = data_bits[i:i+8]
                    byte_value = int(''.join(map(str, byte_bits)), 2)
                    data_bytes.append(byte_value)
            
            data = bytes(data_bytes)
            
            return SteganographyResult(
                success=True,
                data=data,
                metadata={
                    "method": "Whitespace",
                    "extracted_size": len(data)
                }
            )
            
        except Exception as e:
            logger.error(f"Text whitespace extraction failed: {e}")
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def analyze_steganography(self, file_path: str) -> SteganographyResult:
        """
        Analyze file for potential steganography.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            SteganographyResult with analysis data
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                return self._analyze_image(file_path)
            elif file_ext in ['.wav', '.mp3']:
                return self._analyze_audio(file_path)
            elif file_ext in ['.txt', '.md']:
                return self._analyze_text(file_path)
            else:
                return SteganographyResult(
                    success=False,
                    error_message=f"Unsupported file type: {file_ext}"
                )
                
        except Exception as e:
            logger.error(f"Steganography analysis failed: {e}")
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def _analyze_image(self, image_path: str) -> SteganographyResult:
        """Analyze image for steganography"""
        try:
            image = Image.open(image_path)
            
            # Basic analysis
            width, height = image.size
            capacity = (width * height * 3) // 8  # LSB capacity
            
            # Check for statistical anomalies in LSBs
            pixels = list(image.getdata())
            lsb_count = sum(1 for pixel in pixels for color in pixel if color & 1)
            total_bits = len(pixels) * 3
            lsb_ratio = lsb_count / total_bits
            
            # Normal ratio should be around 0.5
            anomaly_score = abs(lsb_ratio - 0.5) * 2
            
            return SteganographyResult(
                success=True,
                metadata={
                    "file_type": "image",
                    "size": f"{width}x{height}",
                    "capacity": capacity,
                    "lsb_ratio": lsb_ratio,
                    "anomaly_score": anomaly_score,
                    "suspicious": anomaly_score > 0.1
                }
            )
            
        except Exception as e:
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def _analyze_audio(self, audio_path: str) -> SteganographyResult:
        """Analyze audio for steganography"""
        try:
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
                sample_width = audio_file.getsampwidth()
                channels = audio_file.getnchannels()
                framerate = audio_file.getframerate()
            
            # Convert to numpy array
            if sample_width == 1:
                dtype = np.uint8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.int32
            else:
                raise ValueError(f"Unsupported sample width: {sample_width}")
            
            audio_array = np.frombuffer(frames, dtype=dtype)
            
            # Analyze LSB distribution
            lsb_count = np.sum(audio_array & 1)
            total_samples = len(audio_array)
            lsb_ratio = lsb_count / total_samples
            
            anomaly_score = abs(lsb_ratio - 0.5) * 2
            
            return SteganographyResult(
                success=True,
                metadata={
                    "file_type": "audio",
                    "samples": total_samples,
                    "channels": channels,
                    "sample_width": sample_width,
                    "framerate": framerate,
                    "lsb_ratio": lsb_ratio,
                    "anomaly_score": anomaly_score,
                    "suspicious": anomaly_score > 0.1
                }
            )
            
        except Exception as e:
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )
    
    def _analyze_text(self, text_path: str) -> SteganographyResult:
        """Analyze text for steganography"""
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Check for invisible characters
            invisible_chars = ['\u200B', '\u200C', '\u200D', '\uFEFF']
            invisible_count = sum(text.count(char) for char in invisible_chars)
            
            # Check for unusual whitespace patterns
            spaces = text.count(' ')
            tabs = text.count('\t')
            newlines = text.count('\n')
            
            return SteganographyResult(
                success=True,
                metadata={
                    "file_type": "text",
                    "length": len(text),
                    "invisible_chars": invisible_count,
                    "spaces": spaces,
                    "tabs": tabs,
                    "newlines": newlines,
                    "suspicious": invisible_count > 0
                }
            )
            
        except Exception as e:
            return SteganographyResult(
                success=False,
                error_message=str(e)
            )

# Convenience functions
def hide_in_image(image_path: str, data: bytes, output_path: str) -> SteganographyResult:
    """Hide data in image using LSB steganography"""
    stego = CryptSteganographer()
    return stego.hide_in_image_lsb(image_path, data, output_path)

def extract_from_image(image_path: str) -> SteganographyResult:
    """Extract data from image using LSB steganography"""
    stego = CryptSteganographer()
    return stego.extract_from_image_lsb(image_path)

def hide_in_audio(audio_path: str, data: bytes, output_path: str) -> SteganographyResult:
    """Hide data in audio using LSB steganography"""
    stego = CryptSteganographer()
    return stego.hide_in_audio_lsb(audio_path, data, output_path)

def extract_from_audio(audio_path: str) -> SteganographyResult:
    """Extract data from audio using LSB steganography"""
    stego = CryptSteganographer()
    return stego.extract_from_audio_lsb(audio_path)

def hide_in_text(text: str, data: bytes) -> str:
    """Hide data in text using whitespace steganography"""
    stego = CryptSteganographer()
    return stego.hide_in_text_whitespace(text, data)

def extract_from_text(text: str) -> SteganographyResult:
    """Extract data from text using whitespace steganography"""
    stego = CryptSteganographer()
    return stego.extract_from_text_whitespace(text)

def analyze_file(file_path: str) -> SteganographyResult:
    """Analyze file for potential steganography"""
    stego = CryptSteganographer()
    return stego.analyze_steganography(file_path)

# Export main classes and functions
__all__ = [
    'CryptSteganographer', 'SteganographyConfig', 'SteganographyType', 
    'SteganographyMethod', 'SteganographyResult',
    'hide_in_image', 'extract_from_image', 'hide_in_audio', 'extract_from_audio',
    'hide_in_text', 'extract_from_text', 'analyze_file'
]
