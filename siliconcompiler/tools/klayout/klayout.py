import os
from pathlib import Path
import platform
import shutil

import siliconcompiler

####################################################################
# Make Docs
####################################################################

def make_docs():
    '''
    Klayout is a production grade viewer and editor of GDSII and
    Oasis data with customizable Python and Ruby interfaces.

    Documentation: https://www.klayout.de

    Sources: https://github.com/KLayout/klayout

    Installation: https://www.klayout.de/build.html

    '''

    chip = siliconcompiler.Chip('<design>')
    chip.load_target('freepdk45_demo')
    chip.set('arg','step','export')
    chip.set('arg','index','<index>')
    setup(chip)

    return chip

####################################################################
# Setup tool
####################################################################

def setup(chip, mode="batch"):
    '''
    Setup function for Klayout
    '''

    tool = 'klayout'
    refdir = 'tools/'+tool
    step = chip.get('arg','step')
    index = chip.get('arg','index')

    if platform.system() == 'Windows':
        klayout_exe = 'klayout_app.exe'
        if not shutil.which(klayout_exe):
            loc_dir = os.path.join(Path.home(), 'AppData', 'Roaming', 'KLayout')
            global_dir = os.path.join(os.path.splitdrive(Path.home())[0],
                                      os.path.sep,
                                      'Program Files (x86)',
                                      'KLayout')
            if os.path.isdir(loc_dir):
                chip.set('tool', tool, 'path', loc_dir)
            elif os.path.isdir(global_dir):
                chip.set('tool', tool, 'path', global_dir)
    elif platform.system() == 'Darwin':
        klayout_exe = 'klayout'
        if not shutil.which(klayout_exe):
            klayout_dir = os.path.join(os.path.sep,
                                       'Applications',
                                       'klayout.app',
                                       'Contents',
                                       'MacOS')
            # different install directory when installed using Homebrew
            klayout_brew_dir = os.path.join(os.path.sep,
                                            'Applications',
                                            'KLayout',
                                            'klayout.app',
                                            'Contents',
                                            'MacOS')
            if os.path.isdir(klayout_dir):
                chip.set('tool', tool, 'path', klayout_dir)
            elif os.path.isdir(klayout_brew_dir):
                chip.set('tool', tool, 'path', klayout_brew_dir)
    else:
        klayout_exe = 'klayout'

    is_show = mode == 'show' or step == 'show'
    is_screenshot = mode == 'screenshot' or step == 'screenshot'
    if is_show or is_screenshot:
        clobber = False
        script = 'klayout_show.py'
        option = ['-nc', '-rm']
    else:
        clobber = False
        script = 'klayout_export.py'
        option = ['-b', '-r']

    chip.set('tool', tool, 'exe', klayout_exe)
    chip.set('tool', tool, 'vswitch', ['-zz', '-v'])
    # Versions < 0.27.6 may be bundled with an incompatible version of Python.
    chip.set('tool', tool, 'version', '>=0.27.6', clobber=clobber)
    chip.set('tool', tool, 'format', 'json', clobber=clobber)
    chip.set('tool', tool, 'refdir', step, index, refdir, clobber=clobber)
    chip.set('tool', tool, 'script', step, index, script, clobber=clobber)
    chip.set('tool', tool, 'option', step, index, option, clobber=clobber)

    # Export GDS with timestamps by default.
    chip.set('tool', tool, 'var', step, index, 'timestamps', 'true', clobber=False)

    design = chip.top()

    # Input/Output requirements for default flow
    if step in ['export']:
        if (not chip.valid('input', 'layout', 'def') or
            not chip.get('input', 'layout', 'def')):
            chip.add('tool', tool, 'input', step, index, design + '.def')
        chip.add('tool', tool, 'output', step, index, design + '.gds')

    # Adding requirements
    if is_show or is_screenshot:
        if chip.valid('tool', tool, 'var', step, index, 'show_filepath'):
            chip.add('tool', tool, 'require', step, index, ",".join(['tool', tool, 'var', step, index, 'show_filepath']))
        else:
            incoming_ext = find_incoming_ext(chip)
            chip.set('tool', tool, 'var', step, index, 'show_filetype', 'str', field="type")
            chip.add('tool', tool, 'require', step, index, ",".join(['tool', tool, 'var', step, index, 'show_filetype']))
            chip.set('tool', tool, 'var', step, index, 'show_filetype', incoming_ext)
            chip.add('tool', tool, 'input', step, index, f'{design}.{incoming_ext}')
        chip.set('tool', tool, 'var', step, index, 'show_exit', 'bool', field="type")
        chip.set('tool', tool, 'var', step, index, 'show_exit', is_screenshot, clobber=False)
        if is_screenshot:
            chip.add('tool', tool, 'output', step, index, design + '.png')
            chip.set('tool', tool, 'var', step, index, 'show_horizontal_resolution', '1024', clobber=False)
            chip.set('tool', tool, 'var', step, index, 'show_vertical_resolution', '1024', clobber=False)
    else:
        targetlibs = chip.get('asic', 'logiclib')
        stackup = chip.get('asic', 'stackup')
        pdk = chip.get('option', 'pdk')
        if bool(stackup) & bool(targetlibs):
            macrolibs = chip.get('asic', 'macrolib')

            chip.add('tool', tool, 'require', step, index, ",".join(['asic', 'logiclib']))
            chip.add('tool', tool, 'require', step, index, ",".join(['asic', 'stackup']))
            chip.add('tool', tool, 'require', step, index,  ",".join(['pdk', pdk, 'layermap', 'klayout', 'def','gds', stackup]))

            for lib in (targetlibs + macrolibs):
                chip.add('tool', tool, 'require', step, index, ",".join(['library', lib, 'output', stackup, 'gds']))
                chip.add('tool', tool, 'require', step, index, ",".join(['library', lib, 'output', stackup, 'lef']))
        else:
            chip.error(f'Stackup and targetlib paremeters required for Klayout.')

    # Log file parsing
    chip.set('tool', tool, 'regex', step, index, 'warnings', r'(WARNING|warning)', clobber=False)
    chip.set('tool', tool, 'regex', step, index, 'errors', r'ERROR', clobber=False)

################################
# Version Check
################################

def parse_version(stdout):
    # KLayout 0.26.11
    return stdout.split()[1]

def find_incoming_ext(chip):

    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    flow = chip.get('option', 'flow')

    supported_ext = ('gds', 'oas', 'def')

    for input_step, input_index in chip.get('flowgraph', flow, step, index, 'input'):
        for ext in supported_ext:
            show_file = chip.find_result(ext, step=input_step, index=input_index)
            if show_file:
                return ext

    # Nothing found, just add last one
    return supported_ext[-1]

##################################################
if __name__ == "__main__":

    chip = make_docs()
    chip.write_manifest("klayout.json")
