from streaming_downloader import StreamingDownloader

url = 'http://proxy-013.dc3.dailymotion.com/sec(ebb2fcb1133be20d6e82e3905cbc8d89)/frag({})/video/819/488/324884918_mp4_h264_aac_hq_1.ts'
path_save = '~/Desktop/Current/DM_example_1/'
subtitles = None
download = 'streaming'
verbose = 2
instance_StreamingDownloader = StreamingDownloader(url, path_save, subtitles=subtitles, download=download, verbose=verbose)

instance_StreamingDownloader.download_all()
instance_StreamingDownloader.assemble_all()
