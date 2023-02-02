import siliconcompiler

def make_docs():
    '''A flow for stitching together hardened blocks without doing any automated
    place-and-route.

    This flow generates a GDS and a netlist for passing to a
    verification/signoff flow.
    '''
    chip = siliconcompiler.Chip('<topmodule>')
    chip.set('option', 'flow', 'asictopflow')
    setup(chip)
    return chip

def setup(chip):
    flow = 'asictopflow'
    chip.node(flow, 'import', 'surelog', 'import')
    chip.node(flow, 'syn', 'yosys', 'syn_asic')
    chip.node(flow, 'export', 'klayout', 'export')
    chip.node(flow, 'merge', 'builtin', 'join')

    chip.edge(flow, 'import', 'export')
    chip.edge(flow, 'import', 'syn')

    chip.edge(flow, 'export', 'merge')
    chip.edge(flow, 'syn', 'merge')

    # Set default goal
    for step in chip.getkeys('flowgraph', flow):
        chip.set('flowgraph', flow, step, '0', 'goal', 'errors', 0)
