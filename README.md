# threaded-bucket-finder

A python script to find S3 Buckets for penetration testing or other engagements. This script uses threading and some looping to limit the number of submitted jobs. This is an attempt to keep the script from consuming too many resources when working with a large input list.

# Usage

```
usage: threaded-bucket-finder.py [-h] -i INPUT -o OUTPUT [-u USERAGENT] [-p PROXY] [-l | --list | --no-list]

Find S3 Buckets and list their root contents if available.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The TXT file to process.
  -o OUTPUT, --output OUTPUT
                        The destination file.
  -u USERAGENT, --useragent USERAGENT
                        The User-Agent value to send.
  -p PROXY, --proxy PROXY
                        A proxy server to use, if any.
  -l, --list, --no-list
```

## -i, --input

The input file should contain the name of the bucket without the AWS domain. e.g. some-bucket and not some-bucket.s3.amazonaws.com.

## -o, --output

The output is in CSV format with quoted fileds.

## -u, --useragent

Sets the "User-Agent" header value. By default, it uses the current MS Edge value.

## -p, --proxy

The proxy server to use, e.g. http://127.0.0.1:8080 or socks5://127.0.0.1:8080

## -l, --list

Will attempt to parse the XML returned by an open bucket to list the contents of the root folder. It will not recursivly list the contents of a bucket.

# Notes

- Does not require an AWS account or boto to work.
- Proxy support, if you need to use a SOCKS5 proxy, you will need to install requests\[socks5\] (python3-socks)
- The list (-l) option will only list the root of a bucket.
- Works for me. Sharing to help others. If you improve it, please submit a pull request.
