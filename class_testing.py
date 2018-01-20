

class A:
    def __init__(self):
        self.a = "Hi"


class B(A):

    def __init__(self):
        A.__init__(self)
        print(A.a)


if __name__ == '__main__':

    B()

