import unittest
import numpy as np
from PIL import Image
from lmdb_cli_tool.utils.utils import np2bytes, str2bytes, bytes2str, bytes2np, pil2bytes, bytes2pil


class TestConvertBytes(unittest.TestCase):
    
    def test_np2bytes(self):
        array = np.array([1, 2, 3, 4], dtype=np.uint64)
        byte_data = np2bytes(array)
        self.assertEqual(byte_data, array.tobytes())
    
    def test_str2bytes(self):
        string = "hello world"
        byte_data = str2bytes(string)
        self.assertEqual(byte_data, string.encode('utf-8'))
    
    def test_bytes2str(self):
        byte_data = b"hello world"
        string = bytes2str(byte_data)
        self.assertEqual(string, byte_data.decode('utf-8'))
    
    def test_bytes2np(self):
        array = np.array([1, 2, 3, 4], dtype=np.uint64)
        byte_data = array.tobytes()
        np_array = bytes2np(byte_data)
        np.testing.assert_array_equal(np_array, array)
    
    def test_pil2bytes(self):
        image = Image.new('RGB', (10, 10), color='red')
        byte_data = pil2bytes(image)
        self.assertIsInstance(byte_data, bytes)
    
    def test_bytes2pil(self):
        image = Image.new('RGB', (10, 10), color='red')
        byte_data = pil2bytes(image)
        pil_image = bytes2pil(byte_data)
        self.assertIsInstance(pil_image, Image.Image)
        self.assertEqual(pil_image.size, image.size)
        self.assertEqual(pil_image.mode, image.mode)


if __name__ == '__main__':
    unittest.main()
