# coding:utf-8
import pdb


def write_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)


def read_file(filename):
    with open(filename, 'r') as f:
        data = f.read()
    return data.strip()


def check_by_read(check_list, message):
    for check_ in check_list:
        check_file = "%s/test.txt" % check_
        if read_file(check_file) != message:
            error_file = "/tmp/errlor.log"
            msg = "check %s check_ error" % check_
            write_file(error_file, msg)


def main():
    num = 15
    message = "miles"
    check_list = list()
    for i in range(1, num):
        check_path = '/data%d' % i
        check_list.append(check_path)

    check_list.append("/data")
    for check_ in check_list:
        check_file = "%s/test.txt" % check_
        write_file(check_file, message)

    check_by_read(check_list, message)


if __name__ == "__main__":
    main()
