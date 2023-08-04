import siliconcompiler


####################################################
# Setup for ICE40 Family FPGAs
####################################################
def setup(chip):
    '''
    Lattice ICE40 FPGAs are a family of small parts
    made by Lattice Semiconductor.  A fully open source
    RTL to bitstream flow for ICE40 is available using
    yosys + nextpnr
    '''

    family = 'ice40'
    vendor = 'lattice'

    syn_tool = 'yosys'
    pnr_tool = 'nextpnr'
    
    lut_size = '4'

    all_fpgas = []
    
    all_part_names = [
        "ice40up5k-sg48",
    ]

    for part_name in all_part_names:
        fpga = siliconcompiler.FPGA(chip, part_name)

        fpga.set('fpga', part_name, 'syntool', syn_tool)
        fpga.set('fpga', part_name, 'pnrtool', pnr_tool)
        
        fpga.set('fpga', part_name, 'vendor', vendor)
        fpga.set('fpga', part_name, 'lutsize', lut_size)

        all_fpgas.append(fpga)
        
    return all_fpgas


#########################
if __name__ == "__main__":
    fpga = setup(siliconcompiler.Chip('<fpga>'))
    fpga.write_manifest(f'{fpga.top()}.json')
