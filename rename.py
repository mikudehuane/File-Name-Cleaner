import re
import os
import os.path as osp
import argparse


def rename(fd, template):
    for fn in os.listdir(fd):
        
        try:
            fn_content, fn_ext = fn.rsplit('.', 1)
        except ValueError as e:
            continue

        match = re.match(template, fn_content)

        if match:
            num = match.group(1)
            out_fn = f'{num}.{fn_ext}'
            out_fp = osp.join(fd, out_fn)
            in_fp = osp.join(fd, fn)
            os.rename(in_fp, out_fp)


class Holder(object):
    def __init__(self, content=None):
        self.content = content


if __name__ == '__main__':
    number = 'num5'

    parser = argparse.ArgumentParser('rename files in directory')
    parser.add_argument(
        '-tmp', '--template', type = str, 
        help = f'数字部分用 {number} 指代，不写扩展名'
    )
    args = parser.parse_args()
    template = Holder(args.template)

    # 修改正则化特殊字符
    def _replace(*symbols):
        for symbol in symbols:
            template.content = template.content.replace(symbol, '\\' + symbol)

    _replace('(', ')', '{', '}', '[', ']', '.', '*', '^', '$', '&', '?')
    template = template.content

    template = template.replace(number, '(\d+)')

    print(f'renaming with template: {template}')
    template = re.compile(template)
    rename('.', template)
