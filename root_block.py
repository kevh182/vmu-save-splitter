class RootBlock:
    fat_location: int
    fat_size: int
    dir_location: int
    dir_size: int
    icon_shape: int
    num_user_blocks: int

    def __init__(self, root_data):
        self.data = root_data
        self.fat_location = self.int_at_location(70)
        self.fat_size = self.int_at_location(72)
        self.dir_location = self.int_at_location(74)
        self.dir_size = self.int_at_location(76)
        self.icon_shape = self.int_at_location(78)
        self.num_user_blocks = self.int_at_location(80)
        
    def int_at_location(self, location):
       return int.from_bytes(self.data[location:location+1], "little")