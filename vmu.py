from root_block import RootBlock
from fat_block import FatBlock
from directory import Directory
from directory_entry import DirectoryEntry
from vmu_file import VmuFile
from user_blocks import UserBlocks
from constants import block_size
import copy

class Vmu:
    def __init__(self, file):
        self.blocks = []
        with open("./import/" + file, "rb") as f:
            while True:
                chunk = f.read(block_size)
                if not chunk:
                    break

                self.blocks.append(chunk)

        self.total_blocks = len(self.blocks)
        last_block = self.total_blocks - 1
        self.root = RootBlock(self.blocks[last_block])
        self.fat = FatBlock(self.blocks, self.root)
        self.directory = Directory(self.blocks, self.root)
        self.user_blocks = UserBlocks(self.blocks, self.root)
    
    def free_blocks(self):
        return self.fat.free_blocks

    def list(self):
        self.directory.list()

    def get_file(self, dir_index):
        entry = self.directory.get_entry(dir_index)
        block_refs = self.fat.get_file_blocks(entry.first_block)
        file = VmuFile(self.blocks, block_refs, entry)

        return file
    
    def add_file(self, file: VmuFile):
        if(self.free_blocks() < file.num_blocks):
            raise Exception("Not enough space on VMU")
        if(self.directory.file_exists(file.dir_entry.file_name)):
            raise Exception("File already exists")

        blocks_to_use = self.fat.get_free_blocks(file.num_blocks, file.is_game)

        new_dir_entry = copy.deepcopy(file.dir_entry)
        new_dir_entry.first_block = blocks_to_use[0]
        
        self.directory.add_entry(new_dir_entry)
        self.fat.allocate_blocks(blocks_to_use)
        self.user_blocks.update_blocks(file.blocks, blocks_to_use)

    def build_vmu(self):
        data = bytearray(0)
        for i in range(0, self.root.num_user_blocks):
            data += self.user_blocks.blocks[i]

        num_root_blocks = 1
        unused_blocks = self.total_blocks - num_root_blocks - self.root.num_user_blocks - (self.fat.start - self.fat.end) - (self.directory.start - self.directory.end)

        data += bytearray(unused_blocks * block_size)

        dir_blocks = self.directory.to_blocks()
        for i in range(len(dir_blocks) - 1, -1, -1):
            data += dir_blocks[i]

        fat_blocks = self.fat.to_blocks()
        for i in range(len(fat_blocks) - 1, -1, -1):
            data += fat_blocks[i]

        data += self.root.data
        return data

    def save_vmu(self, file):
        with open("./export/" + file, "wb") as f:
            f.write(self.build_vmu())

        print("Saved to " + file)

        

        