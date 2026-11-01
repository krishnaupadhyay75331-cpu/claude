set -e
cd "$(dirname "$0")"
for k in aroll matte; do printf "file '%s'\n" ${k}_g0.mp4 ${k}_g1.mp4 ${k}_g2.mp4 ${k}_g3.mp4 > ${k}_list.txt; ffmpeg -v error -y -f concat -safe 0 -i ${k}_list.txt -c copy $k.mp4; done
ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 aroll.mp4
ffmpeg -v error -y -i aroll.mp4 -i matte.mp4 -filter_complex "[1:v]format=gray[m];[0:v][m]alphamerge,format=yuva420p" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 6M -deadline realtime -cpu-used 8 -row-mt 1 -auto-alt-ref 0 ../reel/public/subject.webm
cp aroll.mp4 ../reel/public/aroll.mp4
python3 heads.py
