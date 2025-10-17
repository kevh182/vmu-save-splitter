from .root_block import RootBlock
from typing import List

class UserBlocks:
    def __init__(self, blocks: List[bytearray], root: RootBlock):
        self.blocks = []
        for i in range(0,root.num_user_blocks):
            self.blocks.append(blocks[i])

    def update_blocks(self, blocks: List[bytearray], block_numbers: List[int]):
        if (len(blocks) != len(block_numbers)):
            raise Exception("Not enough blocks to allocate")
        
        for i in range(0, len(blocks)):
            block_to_change = block_numbers[i]
            self.blocks[block_to_change] = blocks[i]