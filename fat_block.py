from constants import block_size
from typing import List
from root_block import RootBlock

free_block = bytearray(b'\xfc\xff')
end_of_file = bytearray(b'\xfa\xff')

class FatBlock:
    def __init__(self, blocks: List[bytearray], root: RootBlock):
        self.data = bytearray(0)
        self.free_blocks = 0
        self.blocks = blocks
        self.root = root
        fat_start = root.fat_location
        fat_end = root.fat_location - root.fat_size
        for i in range(fat_start, fat_end, -1):
            self.data += self.blocks[i]
        self.calc_free_blocks()
        self.start = fat_start
        self.end = fat_end

    def calc_free_blocks(self):
        self.free_blocks = 0
        for i in range(0,self.root.num_user_blocks):
            val = self.val_at_location(i*2)
            if val == free_block:
                self.free_blocks += 1
            # elif val == end_of_file:
            #     print("Block " + str(i) + ": EOF")
            # else:
            #     print("Block " + str(i) + ": Continued at " + str(int.from_bytes(val, "little")))

    def val_at_location(self, location):
       return self.data[location:location+2]
    
    def to_blocks(self):
        blocks = []
        fat_size = self.start - self.end
        for i in range(0, fat_size):
            print(i)
            blocks.append(self.data[i * block_size:(i+1)*block_size])
        return blocks
    
    def allocate_blocks(self, blocks: List[int]):
        for i in range(0, len(blocks)):
            if(i < len(blocks) - 1):
                next_value = blocks[i+1].to_bytes(2, "little")
                self.allocate_block(blocks[i], next_value)
            else:
                self.allocate_block(blocks[i], end_of_file)

    def allocate_block(self, block_number, value: bytearray):
        index = block_number * 2
        self.data[index:index+1] = value[0:1]
        self.data[index+1:index+2] = value[1:2]
        self.calc_free_blocks()
    
    def get_file_blocks(self, first):
        file_blocks = [first]
        location = first * 2
        nextLocation = self.val_at_location(location)
        while nextLocation != end_of_file:
            if(nextLocation == free_block):
                raise Exception("FAT Error")
            int_val = int.from_bytes(nextLocation, "little")
            file_blocks.append(int_val)
            location = int_val * 2
            nextLocation = self.val_at_location(location)
        
        return file_blocks
    
    def get_free_blocks(self, num_blocks, is_game):
        blocks = range(0,self.root.num_user_blocks) if is_game else range(self.root.num_user_blocks-1,-1,-1)
        free_blocks = []
        for i in blocks:
            val = self.val_at_location(i*2)
            if val == free_block:
                free_blocks.append(i)
            if len(free_blocks) >= num_blocks:
                break
        return free_blocks