#! /usr/bin/env python3
import os, sys, time, re



def executeCommand(args):
    for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)  # try to exec program
        except FileNotFoundError:             # ...expected
            pass
    os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
    sys.exit(1)  # terminate with error
    # ...fail quietly


def redirectOutput(args):
    leftCommand = args[args.index(">") + 1:]
    os.close(1)
    sys.stdout = os.open(leftCommand[0], os.O_RDWR)
    os.set_inheritable(1, True)
    return args[:args.index(">")]
    return args


def redirectInput(args):
    rightCommand = args[args.index("<") + 1:]
    os.close(0)
    sys.stdin = os.open(rightCommand[0], os.O_RDONLY)
    os.set_inheritable(0, True)
    return args[:args.index("<")]

def makePipe(args):
    leftCommand = args[:args.index("|")]
    rightCommand = args[args.index("|")+1:]
    pipeR, pipeW = os.pipe()
    rc = os.fork()
    if rc < 0:
        print("error!!!!! in fork")
        sys.exit(1)
    elif rc == 0:
        os.close(1)
        sys.stdout = os.dup(pipeW)
        os.set_inheritable(1, True)
        for fd in (pipeR, pipeW):
            os.close(fd)
        executeCommand(leftCommand)
    else:
        os.close(0)
        sys.stdin = os.dup(pipeR)
        os.set_inheritable(0, True)
        for fd in (pipeR, pipeW):
            os.close(fd)
        executeCommand(rightCommand)



def exitShell(args):
    if args[0] == "exit":
        sys.exit(0)


def cdCommand(args):
    if len(args) == 2 and args[0] == "cd":
        temp = os.getcwd() + args[1]
        os.chdir(os.getcwd() + "/" + args[1])
        return True
    return False
#os.chdir()/
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        args = input(os.getcwd() + ":")
        args = args.split(" ")

        if cdCommand(args):
            continue
        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            exitShell(args)
            if "|" in args:
                makePipe(args)

            if ">" in args:
                args = redirectOutput(args)
                executeCommand(args)
            elif "<" in args:
                args = redirectInput(args)
                executeCommand(args)
            else:
                executeCommand(args)
        else:
            exitShell(args)
            os.wait()





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
