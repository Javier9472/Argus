from multiprocessing import Queue, Process
from multiprocessing.raspberry_tasks import capture_process, compress_process, send_process

def main():
    raw_q = Queue(maxsize=10)
    compressed_q = Queue(maxsize=10)

    p1 = Process(target=capture_process, args=(raw_q,))
    p2 = Process(target=compress_process, args=(raw_q, compressed_q))
    p3 = Process(target=send_process, args=(compressed_q,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

if __name__ == "__main__":
    main()
