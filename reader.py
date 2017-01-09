class Reader():
    """
        Initialises the file to be read and implements a line by line reading
    """
    def __init__(self, file):
        self.f = open(file, "r")

    def read_line(self):
        return self.f.readline()
