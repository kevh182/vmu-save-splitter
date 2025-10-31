from .constants import game_file, data_file
from .directory_entry import DirectoryEntry
from typing import List

class VmuFile:
    def __init__(self, all_blocks, block_refs, dir_entry: DirectoryEntry):
        self.blocks: List[bytearray] = []
        self.dir_entry = dir_entry
        self.is_valid = True
        self.is_japanese = False

        for block_ref in block_refs:
            self.blocks.append(all_blocks[block_ref])

        self.is_game = dir_entry.file_type == game_file
        self.is_data = dir_entry.file_type == data_file

        try:
            self.desc = self.blocks[dir_entry.header_offset][0:16].decode('ascii')
            if(str(dir_entry.file_name) != "ICONDATA_VMS"):
                self.desc_long = self.blocks[dir_entry.header_offset][16:48].decode('ascii')
                self.application = self.blocks[dir_entry.header_offset][48:64].decode('ascii')
        except:
            # Some Japanese games not encoded with ASCII, can be used to identify Japanese saves?
            try:
                self.desc = self.blocks[dir_entry.header_offset][0:16].decode('shift_jis')
                if(str(dir_entry.file_name) != "ICONDATA_VMS"):
                    self.desc_long = self.blocks[dir_entry.header_offset][16:48].decode('shift_jis')
                    self.application = self.blocks[dir_entry.header_offset][48:64].decode('shift_jis')
                self.is_japanese = True
            except:
                self.is_valid = False
        self.num_blocks = len(self.blocks)
        # desc/desc_long padded with spaces so .strip() to remove whitespace, application padded with \x00 so .rstrip("\x00") to remove whitespace
        # 64:66 Number of Icons
        # 66:68 Icon animation speed
        # 68:70 Graphic Eyecatch Type
        # 70:72 CRC
        # 72:76 File size
        # 76:96 Reserved (all zero)
        # 96:128 Icon Palette
        # 128:? Icon Bitmaps
        self.num_icons = int.from_bytes(self.blocks[dir_entry.header_offset][64:66], "little")
        self.eyecatch_type = int.from_bytes(self.blocks[dir_entry.header_offset][68:70], "little")
        self.crc = self.blocks[dir_entry.header_offset][70:72]
        self.file_size = int.from_bytes(self.blocks[dir_entry.header_offset][72:76], "little")
        self.header_size = 128 + (self.num_icons * 512) + self.get_graphic_eyecatch_size()
        self.padding = 0 if self.is_game else (self.num_blocks * 512) - (self.header_size + self.file_size)
    
    def get_graphic_eyecatch_size(self):
        if (self.eyecatch_type == 1):
            return 8064
        elif (self.eyecatch_type == 2):
            return 4544
        elif (self.eyecatch_type == 3):
            return 2048
        else:
            return 0
    
    def calc_crc(self):
        if(self.is_game):
            return b'\x00\x00'

        file_bytes = bytearray()
        bytes_remaining = (self.num_blocks * 512) - self.padding
        for i in range(0, self.num_blocks):
            end_of_block = bytes_remaining if bytes_remaining < 512 else 512
            block = self.blocks[i]
            if(i == self.dir_entry.header_offset):
                file_bytes.extend(block[0:70])
                file_bytes.extend(b'\x00\x00')
                file_bytes.extend(block[72:end_of_block])
            else:
                file_bytes.extend(block[0:end_of_block])
            
            bytes_remaining -= 512
            if(bytes_remaining < 0):
                break

        # adapted from https://mc.pp.se/dc/vms/fileheader.html
        n = 0
        for byte in file_bytes:
            n ^= (byte << 8)
            for c in range(0,8):
                if n & 0x8000:
                    n = ((n << 1) ^ 4129)
                else:
                    n = (n << 1)
        return (n & 0xffff).to_bytes(2, "little")