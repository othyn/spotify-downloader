# spotDL usage examples

## Downloading

??? Song info
    To download a song, run

    ```bash
    spotdl download [trackUrl]
    ```

    example:

    ```bash
    spotdl download https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b
    ```

??? Album info
    To download an album, run

    ```bash
    spotdl download [albumUrl]
    ```

    example:

    ```bash
    spotdl download https://open.spotify.com/album/4yP0hdKOZPNshxUOjY0cZj
    ```

??? Playlist info
    To download a playlist, run

    ```bash
    spotdl download [playlistUrl]
    ```

    example:

    ```bash
    spotdl download https://open.spotify.com/playlist/37i9dQZF1E8UXBoz02kGID
    ```

??? Artist info
    To download all songs from an artist run

    ```bash
    spotdl download [artistUrl]
    ```

    example:

    ```bash
    spotdl download https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ
    ```

??? Search info
    To search for and download a song, run, with quotation marks

    ```bash
    spotdl download '[songQuery]'
    ```

    example:

    ```bash
    spotdl download 'The Weeknd - Blinding Lights'
    ```

??? info "YouTube link with Spotify metadata"
    To download YouTube video with metadata from Spotify, run
    > Noting the quote `"` are required

    ```bash
    spotdl download "YouTubeURL|SpotifyURL"
    ```

    example:

    ```bash
    spotdl download "https://www.youtube.com/watch?v=XXYlFuWEuKI|https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b?si=b5c0790edc8f4904"
    ```

You can queue up multiple download tasks by separating the arguments with spaces

```bash
spotdl download [songQuery1] [albumUrl] [songQuery2] ... (order does not matter)
```

example:

```bash
spotdl download 'The Weeknd - Blinding Lights' https://open.spotify.com/playlist/37i9dQZF1E8UXBoz02kGID ...
```


## Syncing

Sync function for the console. Keep local files up to date with playlists/albums/etc.
This will download new songs and remove the ones that are no longer present in the playlists/albums/etc

??? info "Initialise Synchronisation"
    To create the sync file run

    ```bash
    spotdl sync [query] --save-file [fileName]
    ```

    example:

    ```bash
    spotdl sync https://open.spotify.com/playlist/37i9dQZF1E8UXBoz02kGID --save-file "the-weeknd.sync.spotdl"
    ```

    > Note: The sync file has to end with .spotdl

??? info "Syncing"
    To sync the songs run

    ```bash
    spotdl sync [fileName]
    ```

    example:

    ```bash
    spotdl sync "the-weeknd.sync.spotdl"
    ```

## Saving

Saves the songs metadata to a file for further use.

```bash
spotdl save [query] --save-file [fileName]
```

example:

```bash
spotdl save 'The Weeknd - Blinding Lights' --save-file 'the-weeknd.spotdl'
```

??? info "Preloading"
    Preload the download url to speed up the download process.

    ```bash
    spotdl save [query] --save-file [fileName] --preload
    ```

    example:

    ```bash
    spotdl save 'The Weeknd - Blinding Lights' --save-file 'the-weeknd.spotdl' --preload
    ```

## Web UI (User Interface)

To start the web UI, run

```bash
spotdl web
```

### Download location

By default web ui downloads files to a special directory, to overwrite this behaviour
add option `--web-use-output-dir` this will change to output directory back to `--output`

## Config file

### Config file location

The config file is located at `C:\Users\user\.spotdl\config.json`
or `~/.spotdl/config.json` under linux

> Note: If you want to use XDG_DATA_HOME directory, run `mkdir $XDG_DATA_HOME/spotdl`, next time you run spotdl it will be automatically used.

### Generate a config file

To generate a config file, run

```bash
spotdl --generate-config
```

> Note: This will overwrite the existing config file.

### Loading config

Config file gets loaded automatically if it already exists, or if you've passed `--config` flag

If you don't want config to load automatically change `load_config` option in config file to false

```json
{
    "load_config": false
}
```

### Default config

```json
{
    "client_id": "5f573c9620494bae87890c0f08a60293",
    "client_secret": "212476d9b0f3472eaa762d90b19b0ba8",
    "auth_token": null,
    "user_auth": false,
    "headless": false,
    "cache_path": "/Users/username/.spotdl/.spotipy",
    "no_cache": false,
    "max_retries": 3,
    "audio_providers": [
        "youtube-music"
    ],
    "lyrics_providers": [
        "genius",
        "azlyrics",
        "musixmatch"
    ],
    "playlist_numbering": false,
    "scan_for_songs": false,
    "m3u": null,
    "output": "{artists} - {title}.{output-ext}",
    "overwrite": "skip",
    "search_query": null,
    "ffmpeg": "ffmpeg",
    "bitrate": null,
    "ffmpeg_args": null,
    "format": "mp3",
    "save_file": null,
    "filter_results": true,
    "threads": 4,
    "cookie_file": null,
    "restrict": false,
    "print_errors": false,
    "sponsor_block": false,
    "preload": false,
    "archive": null,
    "load_config": true,
    "log_level": "INFO",
    "simple_tui": false,
    "fetch_albums": false,
    "id3_separator": "/",
    "ytm_data": false,
    "web_use_output_dir": false,
    "port": 8800,
    "host": "localhost",
    "keep_alive": false,
    "allowed_origins": null
}
```

## CLI (Command Line Interface)

### Command line options

```
options:
  -h, --help            show this help message and exit

Main options:
  {download,save,web,sync,meta,url}
                        The operation to perform.
                        download: Download the songs to the disk and embed metadata.
                        save: Saves the songs metadata to a file for further use.
                        web: Starts a web interface to simplify the download process.
                        sync: Removes songs that are no longer present, downloads new ones
                        meta: Update your audio files with metadata
                        url: Get the download URL for songs

  query                 Spotify/YouTube URL for a song/playlist/album/artist/etc. to download.
                        For album searching, include 'album:' and optional 'artist:' tags
                        (ie. 'album:the album name' or 'artist:the artist album: the album').
                        For manual audio matching, you can use the format 'YouTubeURL|SpotifyURL'
                        You can only use album/playlist/tracks urls when downloading/matching youtube urls.
                        When using youtube url without spotify url, you won't be able to use `--fetch-albums` option.

  --audio [{youtube,youtube-music} ...]
                        The audio provider to use. You can provide more than one for fallback.
  --lyrics [{genius,musixmatch,azlyrics,synced} ...]
                        The lyrics provider to use. You can provide more than one for fallback.
  --config              Use the config file to download songs. It's located under C:\Users\user\.spotdl\config.json or ~/.spotdl/config.json under linux
  --search-query SEARCH_QUERY
                        The search query to use, available variables: {title}, {artists}, {artist}, {album}, {album-artist}, {genre}, {disc-number}, {disc-count}, {duration}, {year}, {original-date},
                        {track-number}, {tracks-count}, {isrc}, {track-id}, {publisher}, {list-length}, {list-position}, {list-name}, {output-ext}
  --dont-filter-results
                        Disable filtering results.

Spotify options:
  --user-auth           Login to Spotify using OAuth.
  --client-id CLIENT_ID
                        The client id to use when logging in to Spotify.
  --client-secret CLIENT_SECRET
                        The client secret to use when logging in to Spotify.
  --auth-token AUTH_TOKEN
                        The authorisation token to use directly to log in to Spotify.
  --cache-path CACHE_PATH
                        The path where spotipy cache file will be stored.
  --no-cache            Disable caching (both requests and token).
  --cookie-file COOKIE_FILE
                        Path to cookies file.
  --max-retries MAX_RETRIES
                        The maximum number of retries to perform when getting metadata.

FFmpeg options:
  --ffmpeg FFMPEG       The ffmpeg executable to use.
  --threads THREADS     The number of threads to use when downloading songs.
  --bitrate {auto,disable,8k,16k,24k,32k,40k,48k,64k,80k,96k,112k,128k,160k,192k,224k,256k,320k,0,1,2,3,4,5,6,7,8,9}
                        The constant/variable bitrate to use for the output file. Values from 0 to 9 are variable bitrates. Auto will use the bitrate of the original file. Disable will disable the
                        bitrate option. (In case of m4a and opus files, this option will skip the conversion)
  --ffmpeg-args FFMPEG_ARGS
                        Additional ffmpeg arguments passed as a string.

Output options:
  --format {mp3,flac,ogg,opus,m4a}
                        The format to download the song in.
  --save-file SAVE_FILE
                        The file to save/load the songs data from/to. It has to end with .spotdl. If combined with the download operation, it will save the songs data to the file. Required for
                        save/preload/sync
  --preload             Preload the download url to speed up the download process.
  --output OUTPUT       Specify the downloaded file name format, available variables: {title}, {artists}, {artist}, {album}, {album-artist}, {genre}, {disc-number}, {disc-count}, {duration}, {year},
                        {original-date}, {track-number}, {tracks-count}, {isrc}, {track-id}, {publisher}, {list-length}, {list-position}, {list-name}, {output-ext}
  --m3u [M3U]           Name of the m3u file to save the songs to. Defaults to {list[0]}.m3u If you want to generate a m3u for each list in the query use {list}, If you want to generate a m3u file
                        based on the first list in the query use {list[0]}, (0 is the first list in the query, 1 is the second, etc. songs don't count towards the list number)
  --overwrite {metadata,skip,force}
                        How to handle existing/duplicate files. (When combined with --scan-for-songs force will remove all duplicates, and metadata will only apply metadata to the latest song and
                        will remove the rest. )
  --restrict            Restrict filenames to ASCII only
  --print-errors        Print errors (wrong songs, failed downloads etc) on exit, useful for long playlist
  --sponsor-block       Use the sponsor block to download songs from yt/ytm.
  --archive ARCHIVE     Specify the file name for an archive of already downloaded songs
  --playlist-numbering  Sets each track in a playlist to have the playlist's name as its album, and album art as the playlist's icon
  --scan-for-songs      Scan the output directory for existing files. This option should be combined with the --overwrite option to control how existing files are handled. (Output directory is the
                        last directory that is not a template variable in the output template)
  --fetch-albums        Fetch all albums from songs in query
  --id3-separator ID3_SEPARATOR
                        Change the separator used in the id3 tags. Only supported for mp3 files.
  --ytm-data            Use ytm data instead of spotify data when downloading using ytm link

Web options:
  --host HOST           The host to use for the web server.
  --port PORT           The port to run the web server on.
  --keep-alive          Keep the web server alive even when no clients are connected.
  --allowed-origins [ALLOWED_ORIGINS ...]
                        The allowed origins for the web server.
  --web-use-output-dir  Use the output directory instead of the session directory for downloads. (This might cause issues if you have multiple users using the web-ui at the same time)

Misc options:
  --log-level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,MATCH,DEBUG,NOTSET}
                        Select log level.
  --simple-tui          Use a simple tui.
  --headless            Run in headless mode.

Other options:
  --download-ffmpeg     Download ffmpeg to spotdl directory.
  --generate-config     Generate a config file. This will overwrite current config if present.
  --check-for-updates   Check for new version.
  --profile             Run in profile mode. Useful for debugging.
  --version, -v         Show the version number and exit.
```
