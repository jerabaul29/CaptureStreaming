from __future__ import print_function
import requests
from execute_bash_command import subprocess_cmd
import os
import time
import random


class StreamingDownloader():
    """A class to download streaming."""

    def __init__(self, url, path_save, subtitles=None, download='immediate', verbose=2, start_at_fragment_zero=False):
        """Streaming downloader.

        url: the patterned string url to download. For example:
        'https://something_long/segment{0}_something_long'

        path_save: where to save everything

        subtitles: the url for the subtitles. None if no subtitles to
        download.

        download: the download mode.
        'immediate': all segments will be downloaded at once. This may be suspicious
        'streaming': download segments so that always 120 ahead of the current video
          time, where video time is time since download started.

         verbose: verbosity. Higher is more verbose.
        """

        self.url = url
        self.path_save = path_save
        self.subtitles = subtitles
        self.download = download
        self.verbose = verbose
        self.start_at_fragment_zero = start_at_fragment_zero

        # check if path_save exists, create it / issue warning
        if not os.path.exists(path_save):
            if verbose > 0:
                print('Create path: ' + path_save)

            os.makedirs(path_save)
            os.makedirs(path_save + '/fragments/')
            os.makedirs(path_save + '/subtitles/')

        else:
            user_choice = raw_input('Warning, path already exists! Continue [y/n]: ')
            if user_choice == 'n':
                raise Exception("Interrupted by user; do not overwrite existing path!")

        self.commments_on_use()

        # ----------------------------------------------------------------------
        # parameters to be used in the program but are not given as arguments --
        # ----------------------------------------------------------------------

        # PARAMETERS FOR THE 'streaming' download mode
        # wait XX second before checking again if should try to download
        self.delay_wait = 1
        # add a random time of std deviation XX to the elapsed time since beginning of video
        # in determining if should download again.
        self.random_time = 0.5
        random.seed()
        # Try to ensure at least always XX seconds of buffered video
        self.buffer_time_downloaded = 120

        # performs some sanity checks
        self.check_validity_url_segments()

    def check_validity_url_segments(self):
        """Checks if the url of the segments seem legit; In particular, check
        that the name gets different for different segments names."""

        name_segment_1 = self.url.format(1)
        name_segment_2 = self.url.format(2)

        if self.verbose > 2:
            print("name_segment_1: " + name_segment_1)
            print("name_segment_2: " + name_segment_2)

        if name_segment_1 == name_segment_2:
            print("""\n
                  --------------------------------------
                  WARNING START
                  --------------------------------------
                  Segment 1 and Segment 2 have the exact
                  same name; are you sure you did not
                  forget to replace segment number with
                  {}?

                  The program will now abort
                  --------------------------------------
                  WARNING END
                  --------------------------------------\n""")

            raise Exception("Interrupted by program; segments have identical names")

    def commments_on_use(self):
        """A few comments on the way the user resorts to the program."""

        if self.download == 'immediate':
            print("""\n
                  --------------------------------------
                  WARNING START
                  --------------------------------------
                  You use immediate download; this is of
                  course very different from the normal
                  streaming user, who will download as
                  he needs more video. Therefore, you can
                  easily be recognized as a downloader.

                  Downloading streaming may be illegal,
                  use this code only on websites which
                  Terms of Use accept streaming download.

                  This code comes with no warranty of any
                  sort. You act under your own responsibility.
                  --------------------------------------
                  WARNING END
                  --------------------------------------\n""")

        if self.download == 'streaming':
            print("""\n
                  --------------------------------------
                  WARNING START
                  --------------------------------------
                  You use streaming download; this means
                  that you download at each time about 60
                  seconds in advance compared to the watching
                  time you would be achieving if looking in
                  real time a the video. The program will as
                  a consequence take a long time to download
                  all data (about the real time of the video).

                  The advantage is, this is a bit less obvious
                  streaming download compared with the immediate
                  method. However, this may still differ from
                  the typical behavior of a navigator, i.e.
                  this is not a strong guarantee that a
                  well tuned program cannot detect you as
                  a streaming downloader, and maybe more
                  sophisticated timing should be use / you
                  may still be leaking information that
                  design you as a streaming downloader.

                  Downloading streaming may be illegal,
                  use this code only on websites which
                  Terms of Use accept streaming download.

                  This code comes with no warranty of any
                  sort. You act under your own responsibility.
                  --------------------------------------
                  WARNING END
                  --------------------------------------\n""")

    def obtain_segment(self, segment_number):
        """Request the segment_number obtained by substituting the url
        Check the http status code, if valid save
        Return the http status code"""

        crrt_url = self.url.format(segment_number)
        r = requests.get(crrt_url)
        status_code = str(r.status_code)

        if self.verbose > 1:
            print("request: " + crrt_url + ' | status: ' + status_code)

        if status_code == '200':
            # this is ok
            with open(self.path_save + '/fragments/' + str(segment_number) + '.ts', 'w') as f:
                f.write(r.content)

        return(status_code)

    def obtain_subtitles(self):
        """Obtain the subtitles if applicable"""

        if self.subtitles is not None:
            r = requests.get(self.subtitles)
            status_code = str(r.status_code)

            if self.verbose > 1:
                print("request: " + self.subtitles + ' | status: ' + status_code)

            if status_code == '200':
                # this is ok
                with open(self.path_save + '/subtitles/subs.vtt', 'w') as f:
                    f.write(r.content)

            return(status_code)

        return(-1)

    def download_next_segment(self, crrt_segment):
        """Download next segment, check if it is the end."""

        continue_download = True
        status_crrt = self.obtain_segment(crrt_segment)

        if status_crrt != '200':
            self.last_segment = crrt_segment - 1
            continue_download = False
            if self.verbose > 0:
                print("Found last segment: " + str(self.last_segment))

        return(continue_download)

    def get_time_saved_segment(self, segment_number):
        """Get the start time of the segment_number segment in the complete
        video. Segement segment_number must have been downloaded before."""

        if self.verbose > 1:
            print("Look at information frame 0 in segment " + str(segment_number))

        location_segment = self.path_save + '/fragments/' + str(segment_number) + '.ts'
        command_get_time = ' mplayer -vo null -ao null -identify -frames 0 ' + location_segment + '  2>/dev/null'

        output = subprocess_cmd(command_get_time)

        if self.verbose > 2:
            print('##### INFORMATION OBTAINED #####')
            print(output)
            print('##### END INFORM. OBTAINED #####')

        for line in output.splitlines():

            if self.verbose > 2:
                print(line)

            if line[0: 14] == 'ID_START_TIME=':
                data_ID_START_TIME = line[14:]
                start_time = float(data_ID_START_TIME)

                if self.verbose > 1:
                    print('start_time last segment first frame: ' + str(start_time))

                break

        return(start_time)

    def download_all(self):
        """Download all data necessary for streaming, including if applicable
        subtitles."""

        self.obtain_subtitles()

        # first, try to download segment 0 if should; if not work, it means starts at segment 1
        if self.start_at_fragment_zero:
            status_0 = self.obtain_segment(0)

            if status_0 != '200':
                self.start_zero = False
                if self.verbose > 0:
                    print("start at segment 1")
            else:
                self.start_zero = True
                if self.verbose > 0:
                    print("start at segment 0")

        else:
            self.start_zero = False

        crrt_segment = 1
        continue_download = True

        if self.download == 'immediate':

            while continue_download:
                continue_download = self.download_next_segment(crrt_segment)
                crrt_segment += 1

        if self.download == 'streaming':
            # init time of downloading the first segment
            init_time = time.time()

            # download first segment
            continue_download = self.download_next_segment(crrt_segment)
            crrt_segment += 1

            # now download continuously until reach the end of the stream, but
            # do it as a streaming actor would
            while continue_download:
                time_first_frame_last_segment = self.get_time_saved_segment(crrt_segment - 1)

                time_if_streaming = time.time() - init_time
                random_perturbation = random.gauss(0, self.random_time)
                if self.verbose > 1:
                    print("time in video if streaming: " + str(time_if_streaming))

                lenght_ahead_buffered = time_first_frame_last_segment - time_if_streaming + random_perturbation

                if lenght_ahead_buffered < self.buffer_time_downloaded:
                    continue_download = self.download_next_segment(crrt_segment)
                    crrt_segment += 1

                else:
                    time.sleep(self.delay_wait)

    def convert_subtitles(self):
        """Convert subtitles and save them in the root."""
        if self.subtitles is not None:
            string_command = 'ffmpeg -i ' + self.path_save + '/subtitles/subs.vtt ' + self.path_save + '/subs.srt'
            subprocess_cmd(string_command)

    def assemble_ts(self):
        if self.start_zero:
            start_segment = 0
        else:
            start_segment = 1

        list_segments = []
        for crrt_segment in range(start_segment, self.last_segment + 1):
            list_segments.append(self.path_save + '/fragments/' + str(crrt_segment) + '.ts')

        if self.verbose > 1:
            print("Assembling segments: " + str(list_segments))

        if self.verbose > 0:
            print("Start assembling segments, this can take time...")

        string_all_segments = ' '.join(list_segments)

        string_command = 'cat ' + string_all_segments + ' > ' + self.path_save + '/video.ts'

        subprocess_cmd(string_command)

        if self.verbose > 0:
            print("Done assembling segments!")

    def assemble_all(self):
        """Assemble all .ts together into a readable file and save it in the root
        together with converted subtitles."""

        # convert subtitles
        if self.verbose > 0:
            print("convert subtitles")

        self.convert_subtitles()

        # assemble all .ts
        if self.verbose > 0:
            print("assemble .ts files")

        self.assemble_ts()

        if self.verbose > 0:
            print("Video ready!")
