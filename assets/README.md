# Logo source

`logo.svg` is the site's tree icon: "Circle tree" by awimovic from the Noun
Project (CC BY 3.0), with the project's credit text removed and the viewBox
squared to 100×100. It is kept here rather than in `content/extra/` because it
is far too large (820 KB) to serve; the build publishes the rendered files
instead.

Rendered with ImageMagick:

```bash
# Browser tab icon, six sizes in one file. The small ones get their alpha
# boosted, or the thin branches wash out to a grey disc.
convert -background none -density 600 logo.svg -resize 256x256 png32:i256.png
for s in 16:55 32:75 48:85; do
  convert i256.png -resize ${s%%:*}x${s%%:*} -channel A -level 0%,${s##*:}% +channel png32:i${s%%:*}.png
done
for s in 64 128; do convert i256.png -resize ${s}x${s} png32:i$s.png; done
convert i16.png i32.png i48.png i64.png i128.png i256.png ../content/extra/favicon.ico

# Navbar logo: white, since the bar is dark. 128px for a 32px slot (4x).
sed 's|fill="rgb(0,0,0)"|fill="rgb(255,255,255)"|' logo.svg > /tmp/white.svg
convert -background none -density 900 /tmp/white.svg -resize 128x128 \
        -channel A -level 0%,85% +channel png32:../content/extra/logo-light.png
```
