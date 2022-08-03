# Seven Segment Tile

## Here is the Top level AHDL Seven_segment.py
Shown below is the Tile example class example we derived from the BlackIce Mx nMigen [examples](https://github.com/lawrie/blackicemx_nmigen_examples/tree/main/seven_segment) for the seven segment tile.
```python
{{#include ../../mystorm/examples/seven_segment.py}}
```
## The Seven Segment Tile Driver
The tile driver abstracts the tile resource pinouts handling the low level Hex->7-segment encoding.
```python
{{#include ../../mystorm/tiles/seven_seg_tile.py}}
```
