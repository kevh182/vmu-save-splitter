from vmu import Vmu;

# file_to_open = "MK-51035-50-1.vmu"
# file_to_open = "example.VMU"
file_to_open = "MemoryCard1-1.vmu"

exampleVmu = Vmu("example.VMU")
gameFile = exampleVmu.get_file(22)

# ctVmu = Vmu("MK-51035-50-1.vmu")
# ctFile = ctVmu.get_file(1)
currentVmu = Vmu(file_to_open)
currentVmu.add_file(gameFile)
currentVmu.save_vmu("new_vmu.vmu")