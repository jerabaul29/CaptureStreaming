import time
import argparse
from streaming_downloader import StreamingDownloader


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--path", help="path to save all data", type=str)
    parser.add_argument("-d", "--delay", help="delay in seconds before start of download", type=int, default=0)
    parser.add_argument("-n", "--name", help="name under which to save the video", type=str)
    parser.add_argument("-u", "--url", help="url of the fragments to download; remember \{\} substitution", type=str)
    parser.add_argument("-s", "--subtitles", help="url of subtitles", type=str, default=None)
    parser.add_argument("-v", "--verbose", help="verbosity, 0 (min) to 5 (max)", type=int, default=2)
    parser.add_argument("-m", "--mode", help="download mode: immediate / streaming", type=str, default="streaming")

    args = parser.parse_args()

    url = args.url
    delay = args.delay
    name_video = args.name
    path_save = args.path + '/' + name_video
    subtitles = args.subtitles
    download = args.mode
    verbose = args.verbose

    time.sleep(delay)

    instance_StreamingDownloader = StreamingDownloader(url, path_save, subtitles=subtitles, download=download, verbose=verbose)

    instance_StreamingDownloader.download_all()
    instance_StreamingDownloader.assemble_all()


if __name__ == "__main__":
    main()
