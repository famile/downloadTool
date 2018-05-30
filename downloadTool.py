# coding:utf-8

# 断点下载

import requests, sys, os, re, time


class DownloadManager:
    def __init__(self):
        self.block = 1024
        self.total = 0
        self.size = 0


    def touch(self, filename):
        with open(filename, 'w') as f:
            pass

    def remove_nonchars(self, name):

        (name,_) = name = re.subn(ur'[\\\/\:\*\?\"\<\>\|]', '', name)
        return name

    # 是否支持断点续传
    def support_continue(self, url):
        headers = {
            'Range': 'bytes=0-4'
        }

        try:
            r = requests.head(url, headers=headers)
            crange = r.headers["content-range"]
            print  crange
            # ur  其中 r 表示使用原始字符串，u 表示是 unicode 字符串。
            self.total = int(re.match(ur'^bytes 0-4/(\d+)$', crange).group(1))
            return True
        except:
            pass
        try:
            self.total = int(r.headers['content-length'])
        except:
            self.total = 0
        return False

    def download(self, url, local_filename='', headers={}):
        finish = False
        if len(local_filename) == 0:
            num = len(url)
            if num > 20:
                local_filename = url[-20:]
            else:
                local_filename = url[0:]
                local_filename = self.remove_nonchars(local_filename)

        block = self.block

        tmp_filename = local_filename + '.downtmp'
        size = self.size

        if self.support_continue(url):
            try:
                with open(tmp_filename, 'rb') as f:
                    self.size = int(f.read())
                    size = self.size + 1
            except:
                self.touch(tmp_filename)
            finally:
                headers["Range"] = "bytes=%d-" % self.size
        else:
            self.touch(tmp_filename)
            self.touch(local_filename)
        total = self.total / 1024.0 / 1024

        # 当使用requests的get下载大文件/数据时，建议使用使用stream模式。
        # 当把get函数的stream参数设置成False时，它会立即开始下载文件并放到内存中，如果文件过大，
        # 有可能导致内存不足。
        # 当把get函数的stream参数设置成True时，它不会立即开始下载，当你使用iter_content或iter_lines遍历
        # 内容或访问内容属性时才开始下载。需要注意一点：文件没有下载之前，它也需要保持连接。
        # iter_content：一块一块的遍历要下载的内容
        # iter_lines：一行一行的遍历要下载的内容
        # 使用上面两个函数下载大文件可以防止占用过多的内存，因为每次只下载小部分数据。
        r = requests.get(url, stream=True, verify=False, headers=headers)

        if total > 0:
            print "[+] Size: %.2fM" % (total)
        else:
            print "[+] Size: None"

        start_t = time.time()
        with open(local_filename, 'ab+') as f:
            # 搜索指定size的位置，并将指针移动到这个位置
            f.seek(self.size)
            # 截断数据，保留指定位置之前的数据
            f.truncate()
            try:
                for chunk in r.iter_content(chunk_size=block):
                    if chunk:
                        f.write(chunk)
                        size += len(chunk)
                        # flush()方法, 手动刷新内存中内容到硬盘
                        f.flush()

                    # sys.stdout.write是将str写到流，原封不动，不会像print那样默认end＝'\n'
                    # sys.stdout.write只能输出一个str，而print能输出多个str，且默认sep = ' '（一个空格）
                    # print，默认flush = False.
                    # print还可以直接把值写到file中
                    # flush() 刷新输出
                    sys.stdout.write('\b' * 64 + 'Now: %.2fMB, Total: %.2fMB' % (size / 1024.0 / 1024, total))
                    sys.stdout.flush()
                finish = True
                os.remove(tmp_filename)
                spend = int(time.time() - start_t)
                speed = int((size - self.size) / 1024 / spend)
                sys.stdout.write('\nDownload Finished!\nTotal Time: %ss, Download Speed: %sk/s\n' % (spend, speed))
                sys.stdout.flush()
            except:
                print "\nDownload pause"
            finally:
                if not finish:
                    with open(tmp_filename, 'wb') as f:
                        f.write(str(size))

if __name__ == '__main__':
    DownloadManager().download("http://xunleib.zuida360.com/1804/%E8%A5%BF%E9%83%A8%E4%B8%96%E7%95%8C%E7%AC%AC%E4%BA%8C%E5%AD%A3-01.mp4",headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"})