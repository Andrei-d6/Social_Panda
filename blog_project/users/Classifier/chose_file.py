from multiprocessing.connection import Client


def classify_file(path):
    address = ("localhost", 6007)
    try:
        conn = Client(address, authkey=b"epicpass")
    except ConnectionRefusedError:
        return 1
    conn.send(path)

    if path == "close":
        conn.close()
        return

    score = conn.recv()
    print(score)
    conn.close()
    return score

# if __name__ == '__main__':
#     classify_file(sys.argv[1])
