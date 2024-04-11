class Parent:
    def __new__(cls):
        print(__class__)
        print(cls)

class Child:
    def __new__(cls):
        print(__class__)
        print(cls)

if __name__ == "__main__":
    parent = Child()
    print(parent)