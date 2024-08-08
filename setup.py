import setuptools
import subprocess
from distutils.command.build import build as _build  # isort:skip

class build(_build):
  sub_commands = _build.sub_commands + [('CustomCommands', None)]

CUSTOM_COMMANDS=[['apt-get', 'update'],
                 ['apt-get', '--asuume-yes', 'install', 'libgl1-mesa-glx']]

class CustomCommands(setuptools.Command):
  def RunCustomCommand(self, command_list):
    print('Running command: %s' % command_list)
    p = subprocess.Popen(
        command_list,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    
    stdout_data, _ = p.communicate()
    print('Command output: %s' % stdout_data)
    if p.returncode != 0:
      raise RuntimeError(
          'Command %s failed: exit code: %s' % (command_list, p.returncode))

  def run(self):
    for command in CUSTOM_COMMANDS:
      self.RunCustomCommand(command)




REQUIRED_PACKAGES=['apache-beam', 'apache-beam[gcp]', 'Pillow', 'numpy', 'opencv-python', 'google-cloud-storage']

setuptools.setup(name='pipel', 
      version='1',
      setup_requires=REQUIRED_PACKAGES,
      description='install required packages for the pipeline',
      install_requires=REQUIRED_PACKAGES,
      packages=setuptools.find_packages(),
      include_package_data=True
      cmdclass={'build':build,
                'Customcommands': CustomCommands})
