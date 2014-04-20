#! /usr/bin/env python
import os
from os import path
import subprocess


# http://stackoverflow.com/a/377028/2691632
def exists(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True

    return False


def create_video(input_dir, n_zeros, output_fname,
                 output_dir=None, image_type='jpg', fps=30,
                 overwrite=True, verbose=False):
    file_pattern = '%0{}d.{}'.format(n_zeros, image_type)
    input_pattern = path.join(input_dir, file_pattern)
    if output_dir is None:
        output_dir = input_dir
    output = path.join(output_dir, output_fname + '.mp4')

    if not overwrite and path.isfile(output):
        # user doesn't want to overwrite and the file is already there
        print ('    {} already exists and overwrite is False - '
               'skipping').format(output)
        return

    if verbose:
        vb_cmd = 'info'
    else:
        vb_cmd = 'quiet'

    if exists('avconv'):
        cmd = ['avconv', '-y', '-v', vb_cmd, '-r', str(fps),
               '-i', input_pattern,
               '-b:v', '1000k',
               output]
    elif exists('ffmpeg'):
        cmd = ['ffmpeg', '-y', '-v', vb_cmd, '-r', str(fps),
               '-i', input_pattern,
               output]
    else:
        raise Exception("avconv or ffmpeg are required to use this utility")
    print '    {} -> {}'.format(input_dir, output)
    return subprocess.call(cmd)


def search_for_images(output_dir, dirname, fnames, image_type='jpg'):
    images = [s for s in fnames if s.endswith('.' + image_type)]
    if len(images) != 0:
        root, containing = path.split(dirname)
        image_names = [path.splitext(i)[0] for i in images]
        image_numbers = set(int(x) for x in image_names)
        expected = set(range(len(images)))
        if image_numbers == expected:
            n_zeros = len(image_names[0])
            print ('{} has contiguous {} files'
                   ' in range 0-{} ({} padded)').format(
                dirname, image_type, len(images) - 1, n_zeros)
            create_video(dirname, n_zeros, containing,
                         output_dir=output_dir, image_type=image_type)


def imgtovid(input_dir, output_dir=None):
    if output_dir is None:
        output_dir = path.join(input_dir, 'imgtovid')
    if not path.isdir(output_dir):
        os.makedirs(output_dir)
    path.walk(input_dir, search_for_images, output_dir)


def main(args):
    print args
    imgtovid(args.dir, output_dir=args.output)

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description=r"""
        Recursively search for folders of sequential images and generate
        videos from them. Videos will be named after the containing directory
        structure - e.g.

            dir/foo/bar/001.jpg  -> output/foo_bar.mp4

        Note that this does lead to degenerate cases if you use underscore
        folder names. Currently only supports jpg images but trivial to add
        support for more in the future.
        """)
    parser.add_argument("dir", help="the directory that should be recursively "
                                    "searched")
    parser.add_argument("-o", "--output",
                        help="The folder which should be outputted to. If "
                             "none is provided, set to dir/imgtovid")
    main(parser.parse_args())
