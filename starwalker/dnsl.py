import os
if os.path.exists('./starwalker.py'):
    os.system('python starwalker.py')
else:
    print('starwalker.py not found')
    print('Please download the latest version from https://github.com/ziyang-Bai/Starwalker')
    print('If you have already downloaded the latest version, please run the command "python starwalker.py" in the directory where starwalker.py is located')
    print('If you still cannot run the program, please create an issue on GitHub')
    print('Starwalker D.N.S.L 1.0 24w32a MPL-2.0 license Ziyang-Bai 2024')
    exit()