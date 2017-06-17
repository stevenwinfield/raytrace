import sys
from .result import RenderResult

def main():
    filename = sys.argv[1]
    with open(filename, "rb") as fileobj:
        result = RenderResult.fromfile(fileobj)

    if len(sys.argv) > 2:
        width = int(sys.argv[2])
    else:
        width = None

    if len(sys.argv) > 3:
        height = int(sys.argv[3])
    else:
        height = None

    result.view(width, height)

if __name__ == "__main__":
    main()
