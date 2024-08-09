#
# odgt2yolo.py
# convert odgt format of https://www.crowdhuman.org to YOLO format.
#

import os
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pathlib import Path

import argparse

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory

ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

#print(f'ROOT={ROOT}')

def convert_in_original_format(opt):
	with open(opt.path, 'r') as rf:
		for x in rf:
			aitem = json.loads(x)

			with open(aitem['ID'] + '.txt', 'w') as wf:
#				wf.write(str(aitem))
				jason_object = json.dumps(aitem, indent=4)
				wf.write(jason_object)

def convert_to_yolo_format(opt):
	with open(opt.path, 'r') as rf:
		for x in rf:
			aitem = json.loads(x)

			with open(aitem['ID'] + '.txt', 'w') as wf:

				gtboxes = aitem["gtboxes"]

				which = 'val' if opt.val else 'train'

				image_path = f'/Users/jeong-yungeol/Desktop/vertexai/corwdhuman/train/Images/{aitem["ID"]}.jpg'

				img = Image.open(image_path)

				for af in gtboxes:

					if af["tag"] == 'mask':
						continue

					extra = af['extra']

					try:
						if extra["ignore"] == 1:
							continue

					except KeyError:
						pass

					vbox = af["vbox"]

					center_x = vbox[0] + vbox[2]/2
					center_y = vbox[1] + vbox[3]/2
					width = vbox[2]
					height = vbox[3]

					wf.write(f'0 {(center_x/img.width):.6f} {(center_y/img.height):.6f} {(width/img.width):.6f} {(height/img.height):.06f}\n')

					head_attr = af["head_attr"]

					try:
						if head_attr['ignore'] == 0:

							hbox = af["hbox"]

							center_x = hbox[0] + hbox[2]/2
							center_y = hbox[1] + hbox[3]/2
							width = hbox[2]
							height = hbox[3]

							wf.write(f'1 {(center_x/img.width):.6f} {(center_y/img.height):.6f} {(width/img.width):.6f} {(height/img.height):.06f}\n')

					except KeyError:
						pass

				img.close()


def convert(opt):
	
	if opt.original:
		convert_in_original_format(opt)
	else:
		convert_to_yolo_format(opt)


def usage():
	print(f'usage: python {__file__} filename')


def parse_opt(known=False):
	parser = argparse.ArgumentParser()

	parser.add_argument('--original', action='store_true', help='show in the original format.')
	parser.add_argument('--val', action='store_true', help='val')

	parser.add_argument('path')

	return parser.parse_known_args()[0] if known else parser.parse_args()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		usage()
	else:
		opt = parse_opt()
		convert(opt)
