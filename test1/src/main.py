# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    import csv
    expertise = {'years': 0, 'supposed': 0, 'expert' : 0, "study" : 0, "studies" : 0}
    coersion = {'unless' : 0, 'need' : 0, 'dont' : 0}
    #and so on
    with open('../reddit_vm.csv', mode='r', errors='ignore') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0
        for row in csv_reader:
            curr_body = row[6]  # used to filter to just bodies of messages, current format isnt adaptive to multiple
            # data sets unless we specify format. can be removed at time cost
            word_arr = curr_body.split(" ")
            for word in word_arr:
                # logic to look for stuff
                if expertise.__contains__(word):
                    expertise[word] += 1
                if coersion.__contains__(word):
                    coersion[word] += 1
        print(expertise)
        print(coersion)


if __name__ == '__main__':
    main()
