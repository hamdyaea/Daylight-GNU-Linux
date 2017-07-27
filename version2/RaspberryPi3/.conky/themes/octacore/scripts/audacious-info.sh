#!/bin/bash

## TODO:
## *) Get album art (from web) at each album change (not song change).
## *) Draw background at each song change (not every 3secs).
## *) Create headphones.jpg or something equivalent via imagemagick 
##      on-the-fly

## Author: Anjishnu Sarkar
## Version: 1.0
## Acknowledgement(s):
## *) The imagemagick code to create round background is from the website
##      http://www.imagemagick.org/Usage/thumbnails/#rounded

## Feature(s):
## *) The conky window disappears when audacious is not playing.

## Info:
## *) The script assumes you have an image "folder.jpg" in each of your 
##      music albums.

## Installation:
## *********************
## chmod +x audacious-info.sh
## mkdir -p ~/.conky/shell-scripts/
## mkdir -p ~/.conky/pix/
## cp audacious-info.sh ~/.conky/shell-scripts/

## Next create a music.conkyrc. Copy the following relevant conky parts 
## in ~/.conky/music.conkyrc
## ***************************
## minimum_size 325 120
## text_buffer_size 2048
## imlib_cache_size 0
## border_outer_margin 10
## TEXT
## ${if_running audacious}${execpi 3 ~/.conky/shell-scripts/audacious-info.sh}${endif}
## *********************

Corners=10
Opacity=0.0
BGColor='grey'  ## '#bebebe'
# BGColor='#0000ff'
AlbumArt="folder.jpg"
BackUpArt="headphones.png"

## Do not change anything after this
CharLength=7
StaticWidth=127
MinWidth=335
Height=118
WordCount=0

ListPosition=$(audtool playlist-position)
Status=$(audtool playback-status)
EchoStatus="Audacious 2.5.3 is $Status"

Title=$(audtool playlist-tuple-data title "$ListPosition")
if [ -z "$Title" ];then
    Title=$(basename "$(audtool playlist-song-filename \
            "$ListPosition")" .mp3 | sed 's/%20/ /g')
fi
TitleCount=$(echo "Title: "$Title"" | wc -m)

Album=$(audtool playlist-tuple-data album "$ListPosition")
AlbumCount=$(echo "Album: "$Album"" | wc -m)

Artist=$(audtool playlist-tuple-data artist "$ListPosition")
ArtistCount=$(echo "Artist: "$Artist"" | wc -m)

for varcount in $TitleCount $AlbumCount $ArtistCount 
do
    if [ $varcount -gt $WordCount ];then
        WordCount=$varcount
    fi
done

VarWidth=$(echo "${WordCount}*${CharLength}" | bc)
Width=$(echo ""$StaticWidth"+"$VarWidth"" | bc)

if [ $Width -le $MinWidth ];then
    Width=$MinWidth
fi

mkdir -p ~/.Conky/octacore/images/

DrawBG(){
    convert -size ${Width}x${Height} xc:${BGColor} \
        png:- | convert - \
         \( +clone  -threshold -1 \
            -draw "fill black polygon 0,0 0,"$Corners" "$Corners",0 \
            fill white circle "$Corners","$Corners" "$Corners",0" \
            \( +clone -flip \) -compose Multiply -composite \
            \( +clone -flop \) -compose Multiply -composite \
         \) +matte -compose CopyOpacity -composite  \
        -alpha on -channel RGBA -evaluate multiply ${Opacity} \
         ~/.Conky/octacore/images/audbg.png
}

GetArt(){
    FilePath=$(audtool playlist-tuple-data file-path \
                "$ListPosition" | sed 's/file:\/\///') 
    if [ -f "$FilePath"/"$AlbumArt" ];then
        cp "$FilePath"/"$AlbumArt" ~/.Conky/octacore/images/
    else
        cp ~/.Conky/octacore/images/"$BackUpArt" ~/.Conky/octacore/images/"$AlbumArt"
    fi
}

GetProgress(){
    CurrLen=$(audtool current-song-output-length-seconds)
    TotLen=$(audtool current-song-length-seconds)
    if (( $TotLen )); then
        ProgLen=$(expr $CurrLen \* 100  / $TotLen)
    fi
}

AudaciousInfo(){
    case "$1" in
        bg)         DrawBG ;;
        art)        GetArt ;;
        status)     echo "$EchoStatus" ;;
        title)      echo "$Title" ;;
        artist)     echo "$Artist" ;;
        album)      echo "$Album" ;;
        progress)   GetProgress ;;
    esac
}

# if 
    AudaciousInfo bg
    AudaciousInfo art
    echo -n "\${image ~/.Conky/octacore/images/audbg.png -p 0,0}"
    echo -n "\${image ~/.Conky/octacore/images/"$AlbumArt" -p 9,9 -s 100x100}"
    echo ""
    echo -n "                 "
    echo "\${color red}$EchoStatus"
    echo ""
    echo -n "                 "
    echo -n "\${color red}Title: "
    echo -n "\${color red}"
    AudaciousInfo title
    echo -n "                 "
    echo -n "\${color red}Artist: "
    echo -n "\${color red}"
    AudaciousInfo artist
    echo -n "                 "
    echo -n "\${color red}Album: "
    echo -n "\${color red}"
    AudaciousInfo album
    AudaciousInfo progress
    echo -n "                 "
    echo "\${execbar echo "$ProgLen"}"
    echo ""
# fi
