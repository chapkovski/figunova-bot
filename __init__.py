from termcolor import colored
import shutil


def cp(*x, color='red', center=True):
    columns = shutil.get_terminal_size().columns
    x = ' '.join([str(i) for i in x])
    if center:
        x = x.center(columns, '-')
    print(colored(x, color, 'on_cyan', attrs=['bold']))


