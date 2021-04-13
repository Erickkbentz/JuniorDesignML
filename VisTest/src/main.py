import os

import matplotlib.pyplot as plt
import webbrowser


def main():
    x1 = [1, 2, 3]
    y1 = [2, 4, 1]

    plt.plot(x1, y1, label="line 1")

    x2 = [1, 2, 3]
    y2 = [4, 1, 3]

    plt.plot(x2, y2, label="line 2")

    plt.xlabel('x - axis')
    plt.ylabel('y - axis')

    plt.title('Two lines on same graph!')

    plt.legend()

    plt.savefig('tmpfile.png', format='png')



    html = '<head><meta charset="UTF-8"><title>Test Visualization</title></head>' + '<img src=\'tmpfile.png\'>'
    with open('testVis.html', 'w') as f:
        f.write(html)

    webbrowser.open('file://' + os.path.realpath('testVis.html'))


if __name__ == '__main__':
    main()
