# ComixPDF
Simple util to convert bunch of images into one pdf file using python and PIL

## Installation
### Requirements
Minimal version is python3.7

pip install git+https://github.com/Rud356/ComixPDF

## How to use
If you want to run program in CLI mode you can just use this command inside of 
directory: python -m comix_pdf

In case you want to bypass interface and use it via launch arguments you *must*
at least pass `-p` or `--paths` argument with parameters. To pass paths you have to
wrap them with `""`.

### Inline mode launch arguments
* `--help` - basic help
* `--title` or `-t` - sets title
* `--paths` or `-p` - put after it multiple paths to images or directories with images
that will be included into pdf
* `--output-dir` or `-od` - where final pdf will be stored
* `--resolution` or `-res` - sets printing resolution (in dpi)
* `--quality` or `-q` - sets output images quality inside of pdf (% from original)