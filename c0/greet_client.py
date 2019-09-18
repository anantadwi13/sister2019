import Pyro4


def test_no_ns():
    uri = "PYRO:obj_c3a81e227eae4e05a9e0295633fefb23@localhost:64049"
    gserver = Pyro4.Proxy(uri)
    print(gserver.get_greet('ronaldo'))


def test_with_ns():
    uri = "PYRONAME:greetserver@localhost:7777"
    gserver = Pyro4.Proxy(uri)

    run = True
    while(run):
        type = input("\nCommands:\n\t1 to create file\n\t2 to read file\n\t3 to update file\n\t4 to delete file\n\t5 to show list files\n\t6 to exit\n> ")
        if type == "1":
            filename = input("Filename : ")
            text = input("Content : ")
            print(gserver.create(filename, text))
        elif type == "2":
            filename = input("Filename : ")
            print(gserver.read(filename))
        elif type == "3":
            filename = input("Filename : ")
            text = input("Content : ")
            print(gserver.update(filename, text))
        elif type == "4":
            filename = input("Filename : ")
            print(gserver.delete(filename))
        elif type == "5":
            directory = input("Directory : ")
            print(gserver.list(directory))
        elif type == "6":
            run = False
            print("Exiting!")
        else:
            print("Command not found!")


if __name__=='__main__':
    test_with_ns()
