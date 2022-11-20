from .inline_interface import parser, inline_render

args, _ = parser.parse_known_args()


if len(args.parts_paths):
    from pathlib import Path
    paths: list[str] = list(args.parts_paths)
    title: str = args.title
    output_directory: Path = Path(args.output_dir)
    resolution: int = args.resolution
    quality: int = args.quality

    if resolution < 1:
        raise ValueError("Too low value for printing quality")

    if quality not in range(1, 101):
        raise ValueError(
            "Resolution must be set between 1 and 100 including both ends"
        )

    print('renders')
    inline_render(
        title, paths,
        output_directory,
        quality, resolution
    )

else:
    from .cli_interface import ComixCLI
    ComixCLI()
