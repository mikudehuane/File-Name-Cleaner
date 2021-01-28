import re
import os
import os.path as osp


def rename(fd, template):
    for fn in os.listdir(fd):
        in_fp = osp.join(fd, fn)
        match = re.match(template, fn)

        if match:
            num = match.group(1)
            ext = match.group(2)
            out_fn = f'{num}.{ext}'
            out_fp = osp.join(fd, out_fn)
            os.rename(in_fp, out_fp)


if __name__ == '__main__':
    template = re.compile(r'Shingeki no Kyojin - ([0-9]+) \[BDRip 1280x720\]-muxed\.(mp4)')
    rename('.', template)
