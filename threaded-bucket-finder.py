import argparse
import requests
import concurrent.futures
import threading
from xml.etree import ElementTree
from queue import Queue

def file_writer(filePath, queue):
    with open(filePath, 'w') as file:
        while True:
            line = queue.get()
            if line is None:
                break;
            file.write(line)
            file.flush()
            queue.task_done()
    queue.task_done()

def check_bucket(line, queue):
    if line.strip():
        s = requests.Session()
        if useProxy:
            r = s.head("http://{}.s3.amazonaws.com".format(line.strip()), headers=headers, proxies=proxies, timeout=10)
        else:
            r = s.head("http://{}.s3.amazonaws.com".format(line.strip()), headers=headers, timeout=10)
        if r.status_code == 200:
            if args.list:
                r = s.get("http://{}.s3.amazonaws.com".format(line.strip()), headers=headers, timeout=10)
                tree = ElementTree.fromstring(r.content)
                for node in tree.iter():
                    if "Contents" in node.tag:
                        for child in node.iter():
                            if "Key" in child.tag:
                                queue.put('{}, "{}", "{}"\n'.format(r.url, r.status_code, child.text))
            else:
                queue.put('{}, "{}", ""\n'.format(r.url, r.status_code))
        else:
            queue.put('{}, "{}", ""\n'.format(r.url, r.status_code))
        s.close()
        print('{} : [{}]'.format(r.url, r.status_code))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Find S3 Buckets and list their root contents if available.')
    parser.add_argument("-i", "--input", required=True, type=str, help="The TXT file to process.")
    parser.add_argument("-o", "--output", required=True, type=str, help="The destination file.")
    parser.add_argument("-u", "--useragent", required=False, type=str, help="The User-Agent value to send.")
    parser.add_argument("-p", "--proxy", required=False, type=str, help="A proxy server to use, if any.")
    parser.add_argument("-l", "--list", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    headers = {}

    if args.useragent:
        headers['User-Agent'] = args.useragent
    else:
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"


    if args.proxy:
        useProxy = True
        proxies = { 'http': args.proxy, 'https': args.proxy }
    else:
        useProxy = False

    queue = Queue()
    maxthreads = 10

    bucket_names =  open(args.input, 'r')

    # Start the file writer thread
    writer_thread = threading.Thread(target=file_writer, args=(args.output, queue), daemon=True)
    writer_thread.start()

    # Configure worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers = maxthreads) as executor:
        jobs = {}

        for line in bucket_names:
            job = executor.submit(lambda p: check_bucket(*p), [line, queue])
            jobs[job] = line
            # Loop until a job frees up. If you don't do this and you're using a large input file, you will use a ton of RAM."
            while len(jobs) > 50:
                # loop through completed jobs and delete them from the list.
                for job in concurrent.futures.as_completed(jobs):
                    del jobs[job]

    # Signal file writer that the work is done
    queue.put(None)
    queue.join()

    print("completed")
