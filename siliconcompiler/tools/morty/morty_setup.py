import os
import subprocess
import re
import sys
import siliconcompiler

from siliconcompiler.schema import schema_path

################################
# Setup Tool (pre executable)
################################

def setup_tool(chip, step, index):
    ''' Per tool function that returns a dynamic options string based on
    the dictionary settings.
    '''

    # Standard Setup
    tool = 'morty'
    chip.set('eda', tool, step, index, 'threads', 4)
    chip.set('eda', tool, step, index, 'format', 'cmdline')
    chip.set('eda', tool, step, index, 'copy', 'false')
    chip.set('eda', tool, step, index, 'exe', 'morty')
    chip.set('eda', tool, step, index, 'version', '0.0')
    chip.set('eda', tool, step, index, 'vendor', 'morty')

    # output single file to `morty.v`
    chip.add('eda', tool, step, index, 'option', 'cmdline', '-o morty.v')
    # write additional information to `manifest.json`
    chip.add('eda', tool, step, index, 'option', 'cmdline', '--manifest manifest.json')

    chip.add('eda', tool, step, index, 'option', 'cmdline', '-I ../../../')

    for value in chip.get('ydir'):
        chip.add('eda', tool, step, index, 'option', 'cmdline', '--library-dir ' + schema_path(value))
    for value in chip.get('vlib'):
        chip.add('eda', tool, step, index, 'option', 'cmdline', '--library-file ' + schema_path(value))
    for value in chip.get('idir'):
        chip.add('eda', tool, step, index, 'option', 'cmdline', '-I ' + schema_path(value))
    for value in chip.get('define'):
        chip.add('eda', tool, step, index, 'option', 'cmdline', '-D ' + schema_path(value))
    for value in chip.get('source'):
        # only pickle Verilog or SystemVerilog files
        if value.endswith('.v') or value.endswith('.vh') or \
                value.endswith('.sv') or value.endswith('.svh'):
            chip.add('eda', tool, step, index, 'option', 'cmdline', schema_path(value))

################################
# Post_process (post executable)
################################

def post_process(chip, step, index):
    ''' Tool specific function to run after step execution
    '''

    # detect top module by reading the manifest generated by morty
    top = chip.get('design')
    if top == "" and os.isfile("manifest.json"):
        with open("manifest.json", "r") as manifest:
            data = json.load(manifest)
            if len(data["tops"]) > 1:
                chip.logger.error('Multiple top-level modules found during \
                        import, but sc_design was not set')
                sys.exit()
            if len(data["tops"]) <= 0:
                chip.logger.error('No top-level modules found during \
                        import, and sc_design was not set')
                sys.exit()
            top = data["tops"][0]

    # Hand off `morty.v` and `manifest.json` to the next step
    subprocess.run("cp morty.v " + "outputs/" + top + ".v", shell=True)
    subprocess.run("cp manifest.json " + "outputs/", shell=True)

    return 0

##################################################
if __name__ == "__main__":

    # File being executed
    prefix = os.path.splitext(os.path.basename(__file__))[0]
    output = prefix + '.json'

    # create a chip instance
    chip = siliconcompiler.Chip(defaults=False)
    # load configuration
    setup_tool(chip, step='import', index='0')
    # write out results
    chip.writecfg(output)
